"""Business-logic layer implementing the non-AI API functions from the
Inventory skill spec (.claude/skills/Inventory/SKILL.md). Views call these
functions; they never touch the models directly for anything beyond simple
reads, so the business rules live in one place.
"""
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import F, Q, Sum
from django.utils import timezone

from .models import (
    Bin, CycleCount, CycleCountLine, InventoryAdjustmentRequest,
    InventoryTransaction, Item, ItemCategory, Lot, PhysicalInventory,
    PhysicalInventoryLine, SerialNumberRecord, StockLevel, Warehouse,
)


def _next_no(prefix, model, field_name):
    # count()-based sequence: fine at demo/single-process scale, not concurrency-safe.
    today = timezone.localdate().strftime('%Y%m%d')
    stub = f'{prefix}{today}'
    count = model.objects.filter(**{f'{field_name}__startswith': stub}).count()
    return f'{stub}-{count + 1:04d}'


def _get_stock_level(item, warehouse, for_update=False):
    qs = StockLevel.objects.select_for_update() if for_update else StockLevel.objects
    stock, _ = qs.get_or_create(item=item, warehouse=warehouse)
    return stock


def _record_transaction(transaction_type, item, warehouse, quantity, user, **kwargs):
    return InventoryTransaction.objects.create(
        transaction_no=_next_no('TXN', InventoryTransaction, 'transaction_no'),
        transaction_type=transaction_type,
        item=item,
        warehouse=warehouse,
        quantity=quantity,
        user=user,
        **kwargs,
    )


def _update_average_cost(item, old_qty, old_avg, in_qty, in_cost):
    if item.costing_method == 'STANDARD':
        return
    total_qty = old_qty + in_qty
    if total_qty <= 0:
        return
    new_avg = ((old_qty * old_avg) + (in_qty * Decimal(in_cost))) / total_qty
    item.average_cost = new_avg
    item.save(update_fields=['average_cost'])


# ---------------------------------------------------------------------------
# 1. 商品主檔管理
# ---------------------------------------------------------------------------

def create_item(**fields):
    return Item.objects.create(**fields)


def update_item(item, **fields):
    for key, value in fields.items():
        setattr(item, key, value)
    item.save()
    return item


def delete_item(item):
    item.delete()


def create_item_category(**fields):
    return ItemCategory.objects.create(**fields)


# ---------------------------------------------------------------------------
# 2. 倉庫管理
# ---------------------------------------------------------------------------

def create_warehouse(**fields):
    return Warehouse.objects.create(**fields)


def update_warehouse(warehouse, **fields):
    for key, value in fields.items():
        setattr(warehouse, key, value)
    warehouse.save()
    return warehouse


def delete_warehouse(warehouse):
    warehouse.delete()


def create_bin(warehouse, bin_code, zone='', capacity=None):
    return Bin.objects.create(warehouse=warehouse, bin_code=bin_code, zone=zone, capacity=capacity)


def update_bin(bin_obj, **fields):
    for key, value in fields.items():
        setattr(bin_obj, key, value)
    bin_obj.save()
    return bin_obj


def delete_bin(bin_obj):
    bin_obj.delete()


# ---------------------------------------------------------------------------
# 3. 庫存查詢
# ---------------------------------------------------------------------------

def search_inventory(item=None, warehouse=None, barcode=None, category=None,
                      lot_number=None, serial_no=None, bin_code=None):
    qs = StockLevel.objects.select_related('item', 'warehouse')
    if item:
        qs = qs.filter(item=item)
    if warehouse:
        qs = qs.filter(warehouse=warehouse)
    if barcode:
        qs = qs.filter(item__barcode=barcode)
    if category:
        qs = qs.filter(item__category=category)
    if lot_number:
        qs = qs.filter(item__lots__lot_number=lot_number).distinct()
    if serial_no:
        qs = qs.filter(item__serial_numbers__serial_no=serial_no).distinct()
    if bin_code:
        qs = qs.filter(item__transactions__bin__bin_code=bin_code).distinct()

    results = []
    for stock in qs:
        results.append({
            'item': stock.item,
            'warehouse': stock.warehouse,
            'on_hand': stock.on_hand,
            'available': stock.available,
            'reserved': stock.reserved,
            'in_transit': stock.in_transit,
            'pending_issue': stock.reserved,
            'average_cost': stock.item.average_cost,
            'value': stock.on_hand * stock.item.average_cost,
        })
    return results


# ---------------------------------------------------------------------------
# 4. 入庫管理 Stock Receipt
# ---------------------------------------------------------------------------

@transaction.atomic
def receive_inventory(item, warehouse, quantity, unit_cost, user, reference_document='', bin=None,
                       lot_number=None, lot_expiry=None, lot_manufacture_date=None, supplier_name=''):
    if not warehouse.is_active:
        raise ValidationError('倉庫未啟用，無法入庫。')
    if not item.is_active:
        raise ValidationError('商品未啟用，無法入庫。')
    if quantity <= 0:
        raise ValidationError('入庫數量必須大於零。')
    if item.track_lot and not lot_number:
        raise ValidationError('此商品啟用批號管理，入庫時必須輸入批號。')

    lot = None
    if item.track_lot and lot_number:
        lot, created = Lot.objects.get_or_create(
            item=item, lot_number=lot_number,
            defaults={
                'expiry_date': lot_expiry,
                'manufacture_date': lot_manufacture_date,
                'supplier_name': supplier_name,
                'quantity': 0,
            },
        )
        lot.quantity = F('quantity') + quantity
        lot.save(update_fields=['quantity'])
        lot.refresh_from_db()

    stock = _get_stock_level(item, warehouse, for_update=True)
    old_qty, old_avg = stock.on_hand, item.average_cost
    stock.on_hand = F('on_hand') + quantity
    stock.save(update_fields=['on_hand'])
    stock.refresh_from_db()

    _update_average_cost(item, old_qty, old_avg, quantity, unit_cost)

    return _record_transaction(
        'RECEIPT', item, warehouse, quantity, user,
        unit_cost=unit_cost, reference_document=reference_document, bin=bin, lot=lot,
    )


# ---------------------------------------------------------------------------
# 5. 出庫管理 Stock Issue
# ---------------------------------------------------------------------------

@transaction.atomic
def issue_inventory(item, warehouse, quantity, user, reference_document='', bin=None,
                     lot=None, serial=None, allow_negative=False):
    if quantity <= 0:
        raise ValidationError('出庫數量必須大於零。')
    if not warehouse.is_active or warehouse.is_frozen:
        raise ValidationError('倉庫未啟用或盤點凍結中，無法出庫。')

    stock = _get_stock_level(item, warehouse, for_update=True)
    if not allow_negative and stock.available < quantity:
        raise ValidationError(f'可用庫存不足：可用 {stock.available}，需求 {quantity}。')

    if item.track_lot:
        lot = lot or get_fefo_lot(item)
        if lot is None:
            raise ValidationError('此商品啟用批號管理，且查無可用批號存貨。')
        if lot.is_expired:
            raise ValidationError(f'批號 {lot.lot_number} 已過期，不得出貨，除非經授權。')
        if lot.quantity < quantity:
            raise ValidationError('批號庫存不足。')
        lot.quantity = F('quantity') - quantity
        lot.save(update_fields=['quantity'])

    if item.track_serial and serial is not None:
        serial.status = 'SHIPPED'
        serial.save(update_fields=['status'])

    stock.on_hand = F('on_hand') - quantity
    stock.save(update_fields=['on_hand'])

    return _record_transaction(
        'ISSUE', item, warehouse, -quantity, user,
        unit_cost=item.average_cost, reference_document=reference_document,
        bin=bin, lot=lot, serial_number=serial,
    )


# ---------------------------------------------------------------------------
# 6. 庫存調撥
# ---------------------------------------------------------------------------

@transaction.atomic
def transfer_inventory(item, from_warehouse, to_warehouse, quantity, user,
                        from_bin=None, to_bin=None, reference_document=''):
    if quantity <= 0:
        raise ValidationError('調撥數量必須大於零。')
    if not to_warehouse.is_active:
        raise ValidationError('目的倉庫不存在或未啟用。')

    from_stock = _get_stock_level(item, from_warehouse, for_update=True)
    if from_stock.available < quantity:
        raise ValidationError(f'可用庫存不足：可用 {from_stock.available}，需求 {quantity}。')

    from_stock.on_hand = F('on_hand') - quantity
    from_stock.save(update_fields=['on_hand'])

    to_stock = _get_stock_level(item, to_warehouse, for_update=True)
    to_stock.on_hand = F('on_hand') + quantity
    to_stock.save(update_fields=['on_hand'])

    ref = reference_document or _next_no('XFER', InventoryTransaction, 'transaction_no')
    out_txn = _record_transaction(
        'TRANSFER_OUT', item, from_warehouse, -quantity, user,
        unit_cost=item.average_cost, reference_document=ref, bin=from_bin,
    )
    in_txn = _record_transaction(
        'TRANSFER_IN', item, to_warehouse, quantity, user,
        unit_cost=item.average_cost, reference_document=ref, bin=to_bin,
    )
    return out_txn, in_txn


# ---------------------------------------------------------------------------
# 7. 庫存預留
# ---------------------------------------------------------------------------

@transaction.atomic
def reserve_inventory(item, warehouse, quantity, user, reference_document=''):
    if quantity <= 0:
        raise ValidationError('預留數量必須大於零。')
    stock = _get_stock_level(item, warehouse, for_update=True)
    if stock.available < quantity:
        raise ValidationError(f'可用庫存不足，無法預留：可用 {stock.available}，需求 {quantity}。')
    stock.reserved = F('reserved') + quantity
    stock.save(update_fields=['reserved'])
    return _record_transaction(
        'RESERVE', item, warehouse, quantity, user, reference_document=reference_document,
    )


@transaction.atomic
def release_reservation(item, warehouse, quantity, user, reference_document=''):
    if quantity <= 0:
        raise ValidationError('解除預留數量必須大於零。')
    stock = _get_stock_level(item, warehouse, for_update=True)
    release_qty = min(quantity, stock.reserved)
    stock.reserved = F('reserved') - release_qty
    stock.save(update_fields=['reserved'])
    return _record_transaction(
        'RELEASE', item, warehouse, release_qty, user, reference_document=reference_document,
    )


# ---------------------------------------------------------------------------
# 8. 庫存調整（需理由與核准流程）
# ---------------------------------------------------------------------------

def request_inventory_adjustment(item, warehouse, quantity_delta, reason, requested_by):
    if quantity_delta == 0:
        raise ValidationError('調整數量不得為零。')
    if not reason:
        raise ValidationError('庫存調整必須填寫調整原因。')
    return InventoryAdjustmentRequest.objects.create(
        item=item, warehouse=warehouse, quantity_delta=quantity_delta,
        reason=reason, requested_by=requested_by,
    )


@transaction.atomic
def approve_inventory_adjustment(adjustment_request, approver):
    if adjustment_request.status != 'PENDING':
        raise ValidationError('此調整申請已處理過。')
    stock = _get_stock_level(adjustment_request.item, adjustment_request.warehouse, for_update=True)
    stock.on_hand = F('on_hand') + adjustment_request.quantity_delta
    stock.save(update_fields=['on_hand'])

    adjustment_request.status = 'APPROVED'
    adjustment_request.approved_by = approver
    adjustment_request.decided_at = timezone.now()
    adjustment_request.save(update_fields=['status', 'approved_by', 'decided_at'])

    _record_transaction(
        'ADJUSTMENT', adjustment_request.item, adjustment_request.warehouse,
        adjustment_request.quantity_delta, approver, reason=adjustment_request.reason,
        reference_document=f'ADJ-{adjustment_request.pk}',
    )
    return adjustment_request


def reject_inventory_adjustment(adjustment_request, approver):
    if adjustment_request.status != 'PENDING':
        raise ValidationError('此調整申請已處理過。')
    adjustment_request.status = 'REJECTED'
    adjustment_request.approved_by = approver
    adjustment_request.decided_at = timezone.now()
    adjustment_request.save(update_fields=['status', 'approved_by', 'decided_at'])
    return adjustment_request


# ---------------------------------------------------------------------------
# 9. 循環盤點（Cycle Count）
# ---------------------------------------------------------------------------

def create_cycle_count(warehouse, method, created_by, item_codes=None, top_n=20):
    items = select_cycle_count_items(warehouse, method, item_codes=item_codes, top_n=top_n)
    cycle_count = CycleCount.objects.create(
        count_no=_next_no('CC', CycleCount, 'count_no'),
        warehouse=warehouse, method=method, created_by=created_by,
    )
    for item in items:
        stock = StockLevel.objects.filter(item=item, warehouse=warehouse).first()
        CycleCountLine.objects.create(
            cycle_count=cycle_count, item=item,
            system_qty=stock.on_hand if stock else 0,
        )
    return cycle_count


def select_cycle_count_items(warehouse, method, item_codes=None, top_n=20):
    if item_codes:
        return Item.objects.filter(item_code__in=item_codes)
    stock_qs = StockLevel.objects.filter(warehouse=warehouse).select_related('item')
    if method == 'HIGH_VALUE':
        item_ids = sorted(stock_qs, key=lambda s: s.on_hand * s.item.average_cost, reverse=True)[:top_n]
        return [s.item for s in item_ids]
    if method == 'NEAR_EXPIRY':
        cutoff = timezone.localdate() + timezone.timedelta(days=30)
        return Item.objects.filter(
            lots__expiry_date__isnull=False, lots__expiry_date__lte=cutoff,
        ).distinct()[:top_n]
    if method == 'ABC':
        item_ids = sorted(stock_qs, key=lambda s: s.on_hand * s.item.average_cost, reverse=True)
        return [s.item for s in item_ids[:top_n]]
    return Item.objects.filter(stock_levels__warehouse=warehouse).order_by('?')[:top_n]


def record_cycle_count(cycle_count, counted_qtys):
    """counted_qtys: {cycle_count_line_id: Decimal}"""
    for line in cycle_count.lines.all():
        if line.pk in counted_qtys:
            line.counted_qty = counted_qtys[line.pk]
            line.save(update_fields=['counted_qty'])
    cycle_count.status = 'PENDING_APPROVAL'
    cycle_count.save(update_fields=['status'])
    return cycle_count


@transaction.atomic
def approve_cycle_count(cycle_count, approver):
    if cycle_count.status != 'PENDING_APPROVAL':
        raise ValidationError('此盤點單尚未輸入實盤數量或已處理過。')
    for line in cycle_count.lines.select_related('item').all():
        if line.variance:
            stock = _get_stock_level(line.item, cycle_count.warehouse, for_update=True)
            stock.on_hand = F('on_hand') + line.variance
            stock.save(update_fields=['on_hand'])
            _record_transaction(
                'CYCLE_COUNT', line.item, cycle_count.warehouse, line.variance, approver,
                reference_document=cycle_count.count_no, reason='循環盤點盤差調整',
            )
    cycle_count.status = 'APPROVED'
    cycle_count.approved_by = approver
    cycle_count.save(update_fields=['status', 'approved_by'])
    return cycle_count


# ---------------------------------------------------------------------------
# 10. 全面盤點（Physical Inventory）
# ---------------------------------------------------------------------------

@transaction.atomic
def start_physical_inventory(warehouse, created_by):
    warehouse.is_frozen = True
    warehouse.save(update_fields=['is_frozen'])
    physical_inventory = PhysicalInventory.objects.create(
        count_no=_next_no('PI', PhysicalInventory, 'count_no'),
        warehouse=warehouse, created_by=created_by,
    )
    for stock in StockLevel.objects.filter(warehouse=warehouse).select_related('item'):
        PhysicalInventoryLine.objects.create(
            physical_inventory=physical_inventory, item=stock.item, system_qty=stock.on_hand,
        )
    return physical_inventory


def import_physical_count(physical_inventory, counted_qtys):
    """counted_qtys: {physical_inventory_line_id: Decimal}"""
    for line in physical_inventory.lines.all():
        if line.pk in counted_qtys:
            line.counted_qty = counted_qtys[line.pk]
            line.save(update_fields=['counted_qty'])
    physical_inventory.status = 'PENDING_APPROVAL'
    physical_inventory.save(update_fields=['status'])
    return physical_inventory


@transaction.atomic
def approve_physical_inventory(physical_inventory, approver):
    if physical_inventory.status != 'PENDING_APPROVAL':
        raise ValidationError('此盤點單尚未輸入實盤數量或已處理過。')
    for line in physical_inventory.lines.select_related('item').all():
        if line.variance:
            stock = _get_stock_level(line.item, physical_inventory.warehouse, for_update=True)
            stock.on_hand = F('on_hand') + line.variance
            stock.save(update_fields=['on_hand'])
            _record_transaction(
                'PHYSICAL_COUNT', line.item, physical_inventory.warehouse, line.variance, approver,
                reference_document=physical_inventory.count_no, reason='全面盤點盤差調整',
            )
    physical_inventory.status = 'CLOSED'
    physical_inventory.approved_by = approver
    physical_inventory.save(update_fields=['status', 'approved_by'])
    physical_inventory.warehouse.is_frozen = False
    physical_inventory.warehouse.save(update_fields=['is_frozen'])
    return physical_inventory


# ---------------------------------------------------------------------------
# 11. 批號管理（Lot Management，支援 FEFO / FIFO）
# ---------------------------------------------------------------------------

def manage_lot(item, lot_number, **fields):
    lot, _ = Lot.objects.get_or_create(item=item, lot_number=lot_number, defaults={'quantity': 0})
    for key, value in fields.items():
        setattr(lot, key, value)
    lot.save()
    return lot


def get_fefo_lot(item):
    return Lot.objects.filter(item=item, quantity__gt=0).order_by('expiry_date').first()


def get_fifo_lot(item):
    return Lot.objects.filter(item=item, quantity__gt=0).order_by('manufacture_date').first()


# ---------------------------------------------------------------------------
# 12. 序號管理（Serial Number Management）
# ---------------------------------------------------------------------------

def manage_serial_number(item, serial_no, **fields):
    serial, _ = SerialNumberRecord.objects.get_or_create(item=item, serial_no=serial_no)
    for key, value in fields.items():
        setattr(serial, key, value)
    serial.save()
    return serial


# ---------------------------------------------------------------------------
# 13. 條碼管理
# ---------------------------------------------------------------------------

def generate_barcode(item):
    if not item.barcode:
        item.barcode = f'{item.pk:012d}'
        item.save(update_fields=['barcode'])
    return item.barcode


def scan_barcode(code):
    item = Item.objects.filter(barcode=code).first()
    if item is None:
        return None
    stock_levels = StockLevel.objects.filter(item=item).select_related('warehouse')
    return {'item': item, 'stock_levels': list(stock_levels)}


# ---------------------------------------------------------------------------
# 14. 庫存成本計算
# ---------------------------------------------------------------------------

def calculate_inventory_value(item=None, warehouse=None):
    qs = StockLevel.objects.select_related('item', 'warehouse')
    if item:
        qs = qs.filter(item=item)
    if warehouse:
        qs = qs.filter(warehouse=warehouse)

    breakdown = []
    total = Decimal('0')
    for stock in qs:
        value = stock.on_hand * stock.item.average_cost
        total += value
        breakdown.append({
            'item': stock.item, 'warehouse': stock.warehouse,
            'on_hand': stock.on_hand, 'unit_cost': stock.item.average_cost, 'value': value,
        })
    return {'total_value': total, 'breakdown': breakdown}


# ---------------------------------------------------------------------------
# 15. 補貨管理（Reorder Management）
# ---------------------------------------------------------------------------

def generate_reorder_suggestion(warehouse=None):
    qs = StockLevel.objects.select_related('item', 'warehouse')
    if warehouse:
        qs = qs.filter(warehouse=warehouse)

    suggestions = []
    for stock in qs:
        item = stock.item
        if stock.available <= item.reorder_point:
            suggested_qty = max(item.safety_stock + item.reorder_point - stock.available, Decimal('0'))
            if suggested_qty > 0:
                suggestions.append({
                    'item': item, 'warehouse': stock.warehouse,
                    'available': stock.available, 'reorder_point': item.reorder_point,
                    'safety_stock': item.safety_stock, 'lead_time_days': item.lead_time_days,
                    'suggested_qty': suggested_qty,
                })
    return suggestions


# ---------------------------------------------------------------------------
# 16. 效期管理（Expiration Management）
# ---------------------------------------------------------------------------

def get_expired_lots():
    return Lot.objects.filter(expiry_date__lt=timezone.localdate(), quantity__gt=0).select_related('item')


def get_expiring_lots(days=30):
    today = timezone.localdate()
    return Lot.objects.filter(
        expiry_date__gte=today, expiry_date__lte=today + timezone.timedelta(days=days), quantity__gt=0,
    ).select_related('item')


# ---------------------------------------------------------------------------
# 17. 庫存儀表板（Inventory Dashboard）
# ---------------------------------------------------------------------------

def get_inventory_dashboard():
    stock_qs = StockLevel.objects.select_related('item', 'warehouse')
    total_value = sum((s.on_hand * s.item.average_cost for s in stock_qs), Decimal('0'))

    out_of_stock = [s for s in stock_qs if s.available <= 0]
    overstock = [s for s in stock_qs if s.item.safety_stock and s.on_hand > s.item.safety_stock * 3]

    since = timezone.now() - timezone.timedelta(days=90)
    issue_totals = (
        InventoryTransaction.objects.filter(transaction_type='ISSUE', transaction_date__gte=since)
        .values('item__item_code', 'item__item_name')
        .annotate(total_qty=Sum('quantity'))
        .order_by('total_qty')
    )
    best_sellers = list(reversed(list(issue_totals)))[:10]
    slow_movers = list(issue_totals)[:10]

    moved_item_ids = InventoryTransaction.objects.filter(
        transaction_type='ISSUE', transaction_date__gte=timezone.now() - timezone.timedelta(days=180),
    ).values_list('item_id', flat=True).distinct()
    dead_stock = [s for s in stock_qs if s.on_hand > 0 and s.item_id not in set(moved_item_ids)]

    period_issue_qty = abs(sum(
        (t.quantity for t in InventoryTransaction.objects.filter(transaction_type='ISSUE', transaction_date__gte=since)),
        Decimal('0'),
    ))
    avg_on_hand = (sum((s.on_hand for s in stock_qs), Decimal('0')) / stock_qs.count()) if stock_qs.count() else Decimal('0')
    turnover_rate = (period_issue_qty / avg_on_hand) if avg_on_hand else Decimal('0')

    return {
        'total_inventory_value': total_value,
        'out_of_stock_count': len(out_of_stock),
        'out_of_stock_items': out_of_stock[:20],
        'overstock_count': len(overstock),
        'overstock_items': overstock[:20],
        'best_sellers': best_sellers,
        'slow_movers': slow_movers,
        'dead_stock': dead_stock[:20],
        'dead_stock_count': len(dead_stock),
        'turnover_rate': turnover_rate,
    }


# ---------------------------------------------------------------------------
# 報表（Reports）
# ---------------------------------------------------------------------------

REPORT_TYPES = {
    'value': '庫存價值報表',
    'status': '庫存狀況報表',
    'aging': '庫齡分析報表',
    'abc': 'ABC 分析',
    'slow_moving': '滯銷商品報表',
    'dead_stock': '呆滯庫存報表',
    'ledger': '庫存分類帳',
    'transactions': '庫存異動明細',
    'reorder': '補貨建議報表',
    'turnover': '庫存週轉率報表',
}


def generate_inventory_report(report_type, item=None, warehouse=None, date_from=None, date_to=None):
    if report_type == 'value':
        headers = ['商品', '倉庫', '現有庫存', '平均成本', '庫存價值']
        rows = [[r['item'], r['warehouse'], r['on_hand'], r['unit_cost'], r['value']]
                for r in calculate_inventory_value(item, warehouse)['breakdown']]

    elif report_type == 'status':
        headers = ['商品', '倉庫', '現有庫存', '可用庫存', '已預留', '在途']
        rows = [[r['item'], r['warehouse'], r['on_hand'], r['available'], r['reserved'], r['in_transit']]
                for r in search_inventory(item=item, warehouse=warehouse)]

    elif report_type == 'aging':
        headers = ['商品', '批號', '製造日期', '到期日', '數量', '是否過期']
        lots = Lot.objects.select_related('item').filter(quantity__gt=0)
        if item:
            lots = lots.filter(item=item)
        rows = [[l.item, l.lot_number, l.manufacture_date, l.expiry_date, l.quantity, l.is_expired] for l in lots]

    elif report_type == 'abc':
        headers = ['商品', '倉庫', '庫存價值']
        data = calculate_inventory_value(item, warehouse)['breakdown']
        rows = [[r['item'], r['warehouse'], r['value']] for r in sorted(data, key=lambda r: r['value'], reverse=True)]

    elif report_type in ('slow_moving', 'dead_stock'):
        dashboard = get_inventory_dashboard()
        headers = ['商品代號', '商品名稱', '90天出庫量']
        rows = [[r['item__item_code'], r['item__item_name'], r['total_qty']] for r in dashboard['slow_movers']]

    elif report_type == 'ledger' or report_type == 'transactions':
        headers = ['交易編號', '類型', '商品', '倉庫', '數量', '單位成本', '交易日期', '來源單據', '操作者']
        qs = InventoryTransaction.objects.select_related('item', 'warehouse', 'user')
        if item:
            qs = qs.filter(item=item)
        if warehouse:
            qs = qs.filter(warehouse=warehouse)
        if date_from:
            qs = qs.filter(transaction_date__gte=date_from)
        if date_to:
            qs = qs.filter(transaction_date__lte=date_to)
        rows = [[t.transaction_no, t.get_transaction_type_display(), t.item, t.warehouse, t.quantity,
                 t.unit_cost, t.transaction_date, t.reference_document, t.user] for t in qs]

    elif report_type == 'reorder':
        headers = ['商品', '倉庫', '可用庫存', '再訂購點', '建議採購量']
        rows = [[r['item'], r['warehouse'], r['available'], r['reorder_point'], r['suggested_qty']]
                for r in generate_reorder_suggestion(warehouse)]

    elif report_type == 'turnover':
        dashboard = get_inventory_dashboard()
        headers = ['指標', '數值']
        rows = [['庫存週轉率（近90天）', round(dashboard['turnover_rate'], 2)]]

    else:
        raise ValidationError(f'未知的報表類型：{report_type}')

    return {'title': REPORT_TYPES.get(report_type, report_type), 'headers': headers, 'rows': rows}
