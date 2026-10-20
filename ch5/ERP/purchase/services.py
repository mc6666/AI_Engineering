"""Business-logic layer implementing the non-AI API functions from the
PurchaseOrder skill spec (.claude/skills/PurchaseOrder/SKILL.md). Views call
these functions; business rules live here, not in views or templates.
"""
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from inventory import services as inventory_services

from .models import (
    GoodsReceipt, GoodsReceiptItem, PaymentSchedule, PurchaseOrder, PurchaseOrderItem,
    PurchaseRequisition, PurchaseRequisitionItem, Quotation, RFQ, RFQSupplier, Supplier,
    SupplierInvoice, SupplierReturn,
)

PO_APPROVAL_THRESHOLD = Decimal('100000')
THREE_WAY_MATCH_TOLERANCE = Decimal('0.01')


def _next_no(prefix, model, field_name):
    # count()-based sequence: fine at demo/single-process scale, not concurrency-safe.
    today = timezone.localdate().strftime('%Y%m%d')
    stub = f'{prefix}{today}'
    count = model.objects.filter(**{f'{field_name}__startswith': stub}).count()
    return f'{stub}-{count + 1:04d}'


# ---------------------------------------------------------------------------
# 1-2. 請購單建立與核准
# ---------------------------------------------------------------------------

def create_purchase_requisition(applicant, budget_code, lines, department='', required_date=None, reason=''):
    if not budget_code:
        raise ValidationError('請購單必須填寫預算代碼。')
    for line in lines:
        if line['quantity'] <= 0:
            raise ValidationError('請購數量必須大於零。')
    pr = PurchaseRequisition.objects.create(
        pr_number=_next_no('PR', PurchaseRequisition, 'pr_number'),
        applicant=applicant, department=department, budget_code=budget_code,
        required_date=required_date, reason=reason,
    )
    for line in lines:
        PurchaseRequisitionItem.objects.create(requisition=pr, item=line['item'], quantity=line['quantity'])
    return pr


def add_requisition_line(requisition, item, quantity):
    if requisition.status != 'DRAFT':
        raise ValidationError('僅草稿狀態的請購單可以新增明細。')
    if quantity <= 0:
        raise ValidationError('請購數量必須大於零。')
    return PurchaseRequisitionItem.objects.create(requisition=requisition, item=item, quantity=quantity)


def approve_purchase_requisition(requisition, approver):
    if requisition.status != 'DRAFT':
        raise ValidationError('此請購單已處理過。')
    if not requisition.lines.exists():
        raise ValidationError('請購單至少需要一筆商品明細才能核准。')
    requisition.status = 'APPROVED'
    requisition.approved_by = approver
    requisition.save(update_fields=['status', 'approved_by'])
    return requisition


def reject_purchase_requisition(requisition, approver):
    if requisition.status != 'DRAFT':
        raise ValidationError('此請購單已處理過。')
    requisition.status = 'REJECTED'
    requisition.approved_by = approver
    requisition.save(update_fields=['status', 'approved_by'])
    return requisition


# ---------------------------------------------------------------------------
# 3-4. 詢價（RFQ）與報價比較
# ---------------------------------------------------------------------------

def create_rfq(supplier_ids, quote_deadline=None, requisition=None):
    if not supplier_ids:
        raise ValidationError('詢價單至少需選擇一家供應商。')
    rfq = RFQ.objects.create(
        rfq_number=_next_no('RFQ', RFQ, 'rfq_number'),
        requisition=requisition, quote_deadline=quote_deadline,
    )
    for supplier in Supplier.objects.filter(pk__in=supplier_ids):
        RFQSupplier.objects.create(rfq=rfq, supplier=supplier)
    return rfq


def send_rfq(rfq):
    rfq.status = 'SENT'
    rfq.save(update_fields=['status'])
    rfq.rfq_suppliers.update(sent_at=timezone.now())
    return rfq


def record_quotation(rfq, supplier, item, unit_price, lead_time_days=0, payment_terms='', warranty='', freight=0):
    RFQSupplier.objects.filter(rfq=rfq, supplier=supplier).update(replied=True)
    return Quotation.objects.create(
        rfq=rfq, supplier=supplier, item=item, unit_price=unit_price,
        lead_time_days=lead_time_days, payment_terms=payment_terms, warranty=warranty, freight=freight,
    )


def compare_quotations(rfq):
    rows = []
    for q in rfq.quotations.select_related('supplier', 'item'):
        total_cost = q.unit_price + q.freight
        rows.append({
            'quotation': q, 'supplier': q.supplier, 'item': q.item,
            'unit_price': q.unit_price, 'total_cost': total_cost,
            'lead_time_days': q.lead_time_days, 'payment_terms': q.payment_terms,
            'warranty': q.warranty, 'rating': q.supplier.rating, 'freight': q.freight,
        })
    return rows


def recommend_supplier(rfq):
    rows = compare_quotations(rfq)
    if not rows:
        return None
    return min(rows, key=lambda r: (r['total_cost'], -r['rating'], r['lead_time_days']))


# ---------------------------------------------------------------------------
# 5-10. 採購訂單建立、修改、送審、核准、發送、追蹤
# ---------------------------------------------------------------------------

@transaction.atomic
def create_purchase_order(supplier, buyer, lines, requisition=None, required_date=None,
                           shipping_address='', payment_terms=''):
    if not supplier.is_active:
        raise ValidationError('供應商未啟用，無法建立採購訂單。')
    po = PurchaseOrder.objects.create(
        po_number=_next_no('PO', PurchaseOrder, 'po_number'),
        supplier=supplier, requisition=requisition, buyer=buyer,
        required_date=required_date, shipping_address=shipping_address, payment_terms=payment_terms,
    )
    for line in lines:
        PurchaseOrderItem.objects.create(
            purchase_order=po, item=line['item'], description=line.get('description', ''),
            quantity=line['quantity'], unit_price=line['unit_price'],
            discount=line.get('discount', 0), warehouse=line['warehouse'],
        )
    return po


def add_purchase_order_line(po, item, quantity, unit_price, warehouse, description='', discount=0):
    if po.goods_receipts.exists():
        raise ValidationError('已開始收貨的採購訂單不得修改，除非具有授權。')
    if quantity <= 0:
        raise ValidationError('採購數量必須大於零。')
    return PurchaseOrderItem.objects.create(
        purchase_order=po, item=item, description=description, quantity=quantity,
        unit_price=unit_price, discount=discount, warehouse=warehouse,
    )


def update_purchase_order(po, **fields):
    if po.goods_receipts.exists():
        raise ValidationError('已開始收貨的採購訂單不得修改，除非具有授權。')
    for key, value in fields.items():
        setattr(po, key, value)
    po.save()
    return po


def submit_purchase_order(po):
    if po.status != 'DRAFT':
        raise ValidationError('僅草稿狀態的採購訂單可以送審。')
    if not po.supplier.is_active:
        raise ValidationError('供應商不存在或未啟用。')
    if not po.lines.exists():
        raise ValidationError('採購訂單至少需要一筆商品明細才能送審。')
    po.status = 'SUBMITTED'
    po.save(update_fields=['status'])
    return po


def approve_purchase_order(po, approver=None):
    if po.status != 'SUBMITTED':
        raise ValidationError('僅已送審狀態的採購訂單可以核准。')
    if po.total_amount > PO_APPROVAL_THRESHOLD and approver is None:
        raise ValidationError(f'採購金額超過核准門檻 {PO_APPROVAL_THRESHOLD}，須由主管核准。')
    po.status = 'APPROVED'
    po.approved_by = approver
    po.save(update_fields=['status', 'approved_by'])
    return po


def send_purchase_order(po):
    if po.status != 'APPROVED':
        raise ValidationError('僅已核准狀態的採購訂單可以發送。')
    po.status = 'SENT'
    po.sent_at = timezone.now()
    po.save(update_fields=['status', 'sent_at'])
    return po


def confirm_supplier(po, expected_arrival_date=None):
    po.supplier_confirmed = True
    if expected_arrival_date:
        po.expected_arrival_date = expected_arrival_date
    po.save(update_fields=['supplier_confirmed', 'expected_arrival_date'])
    return po


def track_purchase_order(po):
    return {
        'po': po,
        'supplier_confirmed': po.supplier_confirmed,
        'expected_arrival_date': po.expected_arrival_date,
        'is_delayed': bool(
            po.expected_arrival_date and po.expected_arrival_date < timezone.localdate()
            and po.status not in ('RECEIVED', 'CLOSED', 'CANCELLED')
        ),
        'lines': [
            {'item': l.item, 'quantity': l.quantity, 'received_qty': l.received_qty, 'remaining_qty': l.remaining_qty}
            for l in po.lines.select_related('item')
        ],
    }


# ---------------------------------------------------------------------------
# 11-12. 收貨管理（含部分收貨）
# ---------------------------------------------------------------------------

@transaction.atomic
def receive_goods(po, warehouse, receipt_lines, received_by, allow_overage=False):
    """receipt_lines: [{'po_item': PurchaseOrderItem, 'quantity': Decimal}]"""
    if po.status not in ('APPROVED', 'SENT', 'PARTIALLY_RECEIVED'):
        raise ValidationError('採購訂單尚未核准，無法收貨。')
    lines_to_receive = [l for l in receipt_lines if l['quantity'] and l['quantity'] > 0]
    if not lines_to_receive:
        raise ValidationError('請至少輸入一筆收貨數量。')

    grn = GoodsReceipt.objects.create(
        grn_number=_next_no('GRN', GoodsReceipt, 'grn_number'),
        purchase_order=po, warehouse=warehouse, received_by=received_by,
    )
    for line in lines_to_receive:
        po_item = line['po_item']
        qty = line['quantity']
        if not allow_overage and qty > po_item.remaining_qty:
            raise ValidationError(f'{po_item.item.item_code} 收貨數量不得超過未收貨數量（剩餘 {po_item.remaining_qty}）。')
        GoodsReceiptItem.objects.create(goods_receipt=grn, po_item=po_item, received_qty=qty)
        po_item.received_qty = po_item.received_qty + qty
        po_item.save(update_fields=['received_qty'])

    po.status = 'RECEIVED' if all(l.remaining_qty <= 0 for l in po.lines.all()) else 'PARTIALLY_RECEIVED'
    po.save(update_fields=['status'])
    return grn


def process_partial_receipt(po, warehouse, receipt_lines, received_by):
    return receive_goods(po, warehouse, receipt_lines, received_by)


# ---------------------------------------------------------------------------
# 13-14. 品質驗收 / 退貨給供應商
# ---------------------------------------------------------------------------

@transaction.atomic
def quality_inspection(goods_receipt_item, result, user):
    if result not in ('PASS', 'FAIL', 'RETURN'):
        raise ValidationError('檢驗結果必須為 PASS、FAIL 或 RETURN。')
    if goods_receipt_item.quality_result != 'PENDING':
        raise ValidationError('此收貨明細已完成驗收。')
    goods_receipt_item.quality_result = result
    goods_receipt_item.save(update_fields=['quality_result'])
    if result == 'PASS':
        po_item = goods_receipt_item.po_item
        inventory_services.receive_inventory(
            item=po_item.item, warehouse=goods_receipt_item.goods_receipt.warehouse,
            quantity=goods_receipt_item.received_qty, unit_cost=po_item.unit_price,
            user=user, reference_document=goods_receipt_item.goods_receipt.grn_number,
        )
    return goods_receipt_item


def return_to_supplier(goods_receipt_item, reason, quantity, supplier):
    if quantity <= 0:
        raise ValidationError('退貨數量必須大於零。')
    ret = SupplierReturn.objects.create(
        return_no=_next_no('RTN', SupplierReturn, 'return_no'),
        goods_receipt_item=goods_receipt_item, supplier=supplier, reason=reason, quantity=quantity,
    )
    return ret


# ---------------------------------------------------------------------------
# 15-17. 三方比對 / 供應商發票 / 付款排程
# ---------------------------------------------------------------------------

def three_way_match(po, invoice):
    po_qty = sum((l.quantity for l in po.lines.all()), Decimal('0'))
    grn_qty = sum(
        (l.received_qty for l in GoodsReceiptItem.objects.filter(goods_receipt__purchase_order=po)),
        Decimal('0'),
    )
    po_total = po.total_amount
    qty_match = grn_qty <= po_qty
    price_tolerance = (po_total * THREE_WAY_MATCH_TOLERANCE) if po_total else Decimal('0')
    price_match = abs(po_total - invoice.amount) <= max(price_tolerance, Decimal('0.01'))
    matched = qty_match and price_match and invoice.purchase_order_id == po.pk

    invoice.match_status = 'MATCHED' if matched else 'EXCEPTION'
    invoice.save(update_fields=['match_status'])
    return {
        'matched': matched, 'po_qty': po_qty, 'grn_qty': grn_qty,
        'po_total': po_total, 'invoice_amount': invoice.amount,
    }


def process_supplier_invoice(po, invoice_number, invoice_date, amount, payment_terms=''):
    if po.status not in ('RECEIVED', 'PARTIALLY_RECEIVED'):
        raise ValidationError('採購訂單尚未收貨，無法處理發票。')
    invoice = SupplierInvoice.objects.create(
        invoice_number=invoice_number, purchase_order=po, invoice_date=invoice_date,
        amount=amount, payment_terms=payment_terms,
    )
    po.status = 'INVOICED'
    po.save(update_fields=['status'])
    return invoice


def schedule_payment(invoice, due_date, early_discount=0):
    if invoice.match_status != 'MATCHED':
        raise ValidationError('發票尚未完成三方比對，無法安排付款。')
    return PaymentSchedule.objects.create(
        invoice=invoice, due_date=due_date, amount=invoice.amount, early_discount=early_discount,
    )


def mark_payment_paid(payment_schedule):
    payment_schedule.status = 'PAID'
    payment_schedule.save(update_fields=['status'])
    return payment_schedule


# ---------------------------------------------------------------------------
# 18-19. 結案 / 取消
# ---------------------------------------------------------------------------

def close_purchase_order(po):
    if not all(l.remaining_qty <= 0 for l in po.lines.all()):
        raise ValidationError('尚未全部收貨，無法結案。')
    if not po.invoices.exists():
        raise ValidationError('尚未處理供應商發票，無法結案。')
    if po.invoices.exclude(payment_schedules__status='PAID').exists():
        raise ValidationError('仍有未付款餘額，無法結案。')
    po.status = 'CLOSED'
    po.save(update_fields=['status'])
    return po


def cancel_purchase_order(po):
    if po.goods_receipts.exists():
        raise ValidationError('已開始收貨的採購訂單不得取消。')
    po.status = 'CANCELLED'
    po.save(update_fields=['status'])
    return po


# ---------------------------------------------------------------------------
# 20. 採購訂單查詢
# ---------------------------------------------------------------------------

def search_purchase_orders(po_number=None, supplier=None, buyer=None, item=None,
                            date_from=None, date_to=None, status=None):
    qs = PurchaseOrder.objects.select_related('supplier', 'buyer')
    if po_number:
        qs = qs.filter(po_number__icontains=po_number)
    if supplier:
        qs = qs.filter(supplier=supplier)
    if buyer:
        qs = qs.filter(buyer=buyer)
    if item:
        qs = qs.filter(lines__item=item).distinct()
    if date_from:
        qs = qs.filter(order_date__gte=date_from)
    if date_to:
        qs = qs.filter(order_date__lte=date_to)
    if status:
        qs = qs.filter(status=status)
    return qs


# ---------------------------------------------------------------------------
# 供應商績效評分卡
# ---------------------------------------------------------------------------

def generate_supplier_scorecard(supplier):
    pos = PurchaseOrder.objects.filter(supplier=supplier, status__in=['RECEIVED', 'PARTIALLY_RECEIVED', 'INVOICED', 'CLOSED'])
    total_pos = pos.count()

    on_time = 0
    lead_times = []
    for po in pos:
        last_receipt = po.goods_receipts.order_by('-received_date').first()
        if po.expected_arrival_date and last_receipt:
            if last_receipt.received_date.date() <= po.expected_arrival_date:
                on_time += 1
        if po.order_date and po.expected_arrival_date:
            lead_times.append((po.expected_arrival_date - po.order_date).days)

    quality_lines = GoodsReceiptItem.objects.filter(
        po_item__purchase_order__supplier=supplier,
    ).exclude(quality_result='PENDING')
    passed = quality_lines.filter(quality_result='PASS').count()
    quality_total = quality_lines.count()

    total_purchase_amount = sum((po.total_amount for po in pos), Decimal('0'))
    returns_count = SupplierReturn.objects.filter(supplier=supplier).count()

    return {
        'supplier': supplier,
        'total_pos': total_pos,
        'on_time_delivery_rate': (Decimal(on_time) / total_pos * 100) if total_pos else Decimal('0'),
        'quality_pass_rate': (Decimal(passed) / quality_total * 100) if quality_total else Decimal('0'),
        'avg_lead_time_days': (sum(lead_times) / len(lead_times)) if lead_times else 0,
        'total_purchase_amount': total_purchase_amount,
        'return_rate': (Decimal(returns_count) / total_pos * 100) if total_pos else Decimal('0'),
    }


# ---------------------------------------------------------------------------
# 庫存管理技能（重用 inventory app，不重寫邏輯）
# ---------------------------------------------------------------------------

def check_inventory(item=None, warehouse=None):
    return inventory_services.search_inventory(item=item, warehouse=warehouse)


def generate_reorder_suggestion(warehouse=None):
    return inventory_services.generate_reorder_suggestion(warehouse=warehouse)


# ---------------------------------------------------------------------------
# 採購儀表板
# ---------------------------------------------------------------------------

def get_procurement_dashboard():
    open_pos = PurchaseOrder.objects.exclude(status__in=['CLOSED', 'CANCELLED'])
    overdue = [
        po for po in open_pos
        if po.expected_arrival_date and po.expected_arrival_date < timezone.localdate()
        and po.status not in ('RECEIVED', 'CLOSED', 'CANCELLED')
    ]
    return {
        'open_po_count': open_pos.count(),
        'pending_approval_count': PurchaseOrder.objects.filter(status='SUBMITTED').count(),
        'overdue_count': len(overdue),
        'overdue_pos': overdue[:20],
        'unpaid_invoice_count': SupplierInvoice.objects.exclude(payment_schedules__status='PAID').count(),
        'reorder_suggestions': generate_reorder_suggestion()[:10],
    }
