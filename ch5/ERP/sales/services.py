"""Business-logic layer implementing the non-AI API functions from the
Sales Order skill spec (.claude/skills/SalesOrder/SKILL.md). Views call these
functions; models stay dumb data holders.
"""
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Sum
from django.utils import timezone

import inventory.services as inv

from .models import ARInvoice, Customer, PickingList, PickingListLine, SalesOrder, SalesOrderItem, Shipment

SO_APPROVAL_THRESHOLD = Decimal('100000')
VAT_RATE = Decimal('0.05')


def _next_no(prefix, model, field_name):
    # count()-based sequence: fine at demo/single-process scale, not concurrency-safe.
    today = timezone.localdate().strftime('%Y%m%d')
    stub = f'{prefix}{today}'
    count = model.objects.filter(**{f'{field_name}__startswith': stub}).count()
    return f'{stub}-{count + 1:04d}'


# ---------------------------------------------------------------------------
# 1. 建立銷售訂單
# ---------------------------------------------------------------------------

@transaction.atomic
def create_sales_order(customer, salesperson, items, order_date=None, required_date=None, shipping_address=''):
    if not customer.is_active:
        raise ValidationError('客戶未啟用，無法建立訂單。')
    if not items:
        raise ValidationError('銷售訂單至少須有一項商品。')
    for line in items:
        if line['quantity'] <= 0:
            raise ValidationError('訂購數量必須大於零。')
        if not line['warehouse'].is_active:
            raise ValidationError('出貨倉庫不存在或未啟用。')

    order = SalesOrder.objects.create(
        so_number=_next_no('SO', SalesOrder, 'so_number'),
        customer=customer, salesperson=salesperson,
        order_date=order_date or timezone.localdate(), required_date=required_date,
        shipping_address=shipping_address or customer.shipping_address,
    )
    for line in items:
        SalesOrderItem.objects.create(
            sales_order=order, item=line['item'],
            description=line.get('description', '') or line['item'].item_name,
            quantity=line['quantity'], unit_price=line['unit_price'],
            discount=line.get('discount', 0), warehouse=line['warehouse'],
        )
    calculate_pricing(order)
    return order


# ---------------------------------------------------------------------------
# 2 / 3. 修改 / 刪除銷售訂單
# ---------------------------------------------------------------------------

def update_sales_order(order, **fields):
    if order.status in ('SHIPPED', 'INVOICED', 'CLOSED'):
        raise ValidationError('已出貨或已開立發票的訂單不得修改。')
    for key, value in fields.items():
        setattr(order, key, value)
    order.save()
    calculate_pricing(order)
    return order


def delete_sales_order(order):
    if order.status != 'DRAFT':
        raise ValidationError('僅能刪除狀態為草稿的訂單。')
    order.delete()


# ---------------------------------------------------------------------------
# 4. 送出訂單
# ---------------------------------------------------------------------------

def submit_order(order, allow_backorder=False):
    if order.status != 'DRAFT':
        raise ValidationError('僅能送出狀態為草稿的訂單。')
    credit_result = check_customer_credit(order.customer, order.total_amount)
    if not credit_result['approved']:
        raise ValidationError(f'客戶信用檢查未通過：{credit_result["reason"]}')
    if not allow_backorder:
        for line in order.items.all():
            result = check_inventory(line.item, line.warehouse, line.quantity)
            if result['available'] < line.quantity:
                raise ValidationError(
                    f'商品 {line.item} 於倉庫 {line.warehouse} 可用庫存不足：'
                    f'可用 {result["available"]}，需求 {line.quantity}。'
                )
    order.status = 'OPEN'
    order.save(update_fields=['status'])
    return order


# ---------------------------------------------------------------------------
# 5. 訂單核准
# ---------------------------------------------------------------------------

@transaction.atomic
def approve_order(order, approver=None):
    if order.status != 'OPEN':
        raise ValidationError('僅能核准狀態為已開立的訂單。')
    if order.total_amount > SO_APPROVAL_THRESHOLD and approver is None:
        raise ValidationError('訂單金額超過核准門檻，須由主管核准。')
    order.status = 'APPROVED'
    order.save(update_fields=['status'])
    reserve_order_inventory(order)
    return order


# ---------------------------------------------------------------------------
# 6. 庫存檢查
# ---------------------------------------------------------------------------

def check_inventory(item, warehouse, quantity=None):
    results = inv.search_inventory(item=item, warehouse=warehouse)
    row = results[0] if results else None
    return {
        'available': row['available'] if row else Decimal('0'),
        'reserved': row['reserved'] if row else Decimal('0'),
        'in_transit': row['in_transit'] if row else Decimal('0'),
        'expected_arrival_date': None,
    }


# ---------------------------------------------------------------------------
# 7. 預留庫存
# ---------------------------------------------------------------------------

@transaction.atomic
def reserve_order_inventory(order):
    if order.status != 'APPROVED':
        raise ValidationError('僅能為已核准的訂單預留庫存。')
    for line in order.items.all():
        inv.reserve_inventory(
            item=line.item, warehouse=line.warehouse, quantity=line.quantity,
            user=order.salesperson, reference_document=order.so_number,
        )
    return order


def release_order_inventory(order, user):
    for line in order.items.all():
        inv.release_reservation(
            item=line.item, warehouse=line.warehouse, quantity=line.quantity,
            user=user, reference_document=order.so_number,
        )


# ---------------------------------------------------------------------------
# 8 / 9. 價格計算 / 稅額計算
# ---------------------------------------------------------------------------

def calculate_pricing(order):
    subtotal = order.subtotal
    order.total_amount = subtotal - order.discount + order.freight
    order.save(update_fields=['total_amount'])
    return {'subtotal': subtotal, 'discount': order.discount, 'freight': order.freight, 'total': order.total_amount}


def calculate_tax(order):
    # VAT is included in total_amount; only extracted when printing the invoice.
    amount_excl_tax = (order.total_amount / (1 + VAT_RATE)).quantize(Decimal('0.01'))
    vat_amount = order.total_amount - amount_excl_tax
    return {'amount_excl_tax': amount_excl_tax, 'vat_amount': vat_amount, 'amount_incl_tax': order.total_amount}


# ---------------------------------------------------------------------------
# 10. 客戶信用檢查
# ---------------------------------------------------------------------------

def check_customer_credit(customer, additional_amount=Decimal('0'), override=False):
    if override:
        return {'approved': True, 'reason': '已授權覆核。'}
    projected = customer.outstanding_balance + additional_amount
    if projected > customer.credit_limit:
        return {'approved': False, 'reason': f'超過信用額度：額度 {customer.credit_limit}，預計餘額 {projected}。'}
    return {'approved': True, 'reason': ''}


# ---------------------------------------------------------------------------
# 11. 產生揀貨單
# ---------------------------------------------------------------------------

@transaction.atomic
def generate_picking_list(order, created_by):
    if order.status != 'APPROVED':
        raise ValidationError('僅能為已核准的訂單產生揀貨單。')
    if hasattr(order, 'picking_list'):
        raise ValidationError('此訂單已產生揀貨單。')
    picking_list = PickingList.objects.create(sales_order=order, created_by=created_by)
    for line in order.items.all():
        PickingListLine.objects.create(
            picking_list=picking_list, item=line.item, warehouse=line.warehouse, pick_qty=line.quantity,
        )
    order.status = 'PICKING'
    order.save(update_fields=['status'])
    return picking_list


# ---------------------------------------------------------------------------
# 12. 出貨管理
# ---------------------------------------------------------------------------

@transaction.atomic
def create_shipment(order, user, tracking_number='', carrier='', ship_date=None):
    if order.status not in ('PICKING', 'PACKED'):
        raise ValidationError('僅能對揀貨中或包裝中的訂單建立出貨。')
    shipment = Shipment.objects.create(
        sales_order=order, shipment_no=_next_no('SHP', Shipment, 'shipment_no'),
        tracking_number=tracking_number, carrier=carrier, ship_date=ship_date or timezone.localdate(),
    )
    for line in order.items.all():
        inv.release_reservation(
            item=line.item, warehouse=line.warehouse, quantity=line.quantity,
            user=user, reference_document=shipment.shipment_no,
        )
        inv.issue_inventory(
            item=line.item, warehouse=line.warehouse, quantity=line.quantity,
            user=user, reference_document=shipment.shipment_no,
        )
    order.status = 'SHIPPED'
    order.save(update_fields=['status'])
    return shipment


# ---------------------------------------------------------------------------
# 13. 開立發票
# ---------------------------------------------------------------------------

@transaction.atomic
def create_invoice(order):
    if order.status != 'SHIPPED':
        raise ValidationError('僅能對已出貨的訂單開立發票。')
    invoice = ARInvoice.objects.create(
        sales_order=order, invoice_no=_next_no('INV', ARInvoice, 'invoice_no'), amount=order.total_amount,
    )
    order.customer.outstanding_balance += order.total_amount
    order.customer.save(update_fields=['outstanding_balance'])
    order.status = 'INVOICED'
    order.save(update_fields=['status'])
    return invoice


def record_payment(invoice, amount):
    if amount <= 0:
        raise ValidationError('收款金額必須大於零。')
    invoice.paid_amount += amount
    invoice.save(update_fields=['paid_amount'])
    invoice.sales_order.customer.outstanding_balance -= amount
    invoice.sales_order.customer.save(update_fields=['outstanding_balance'])
    return invoice


# ---------------------------------------------------------------------------
# 14. 取消訂單
# ---------------------------------------------------------------------------

@transaction.atomic
def cancel_order(order, user):
    if order.status in ('SHIPPED', 'INVOICED', 'CLOSED'):
        raise ValidationError('已出貨或已開立發票的訂單不得直接取消，須透過退貨或折讓流程處理。')
    if order.status in ('APPROVED', 'PICKING', 'PACKED'):
        release_order_inventory(order, user)
    order.status = 'CANCELLED'
    order.save(update_fields=['status'])
    return order


# ---------------------------------------------------------------------------
# 15. 結案
# ---------------------------------------------------------------------------

def close_order(order):
    if order.status != 'INVOICED':
        raise ValidationError('須所有商品皆已出貨且發票皆已完成，才能結案。')
    order.status = 'CLOSED'
    order.save(update_fields=['status'])
    return order


# ---------------------------------------------------------------------------
# 16. 訂單查詢
# ---------------------------------------------------------------------------

def search_sales_orders(customer=None, so_number=None, item=None, date_from=None, date_to=None,
                         status=None, salesperson=None):
    qs = SalesOrder.objects.select_related('customer', 'salesperson')
    if customer:
        qs = qs.filter(customer=customer)
    if so_number:
        qs = qs.filter(so_number__icontains=so_number)
    if item:
        qs = qs.filter(items__item=item).distinct()
    if date_from:
        qs = qs.filter(order_date__gte=date_from)
    if date_to:
        qs = qs.filter(order_date__lte=date_to)
    if status:
        qs = qs.filter(status=status)
    if salesperson:
        qs = qs.filter(salesperson=salesperson)
    return qs


# ---------------------------------------------------------------------------
# 17. 複製訂單
# ---------------------------------------------------------------------------

@transaction.atomic
def duplicate_order(order, salesperson):
    items = [
        {'item': line.item, 'quantity': line.quantity, 'unit_price': line.unit_price,
         'discount': line.discount, 'warehouse': line.warehouse, 'description': line.description}
        for line in order.items.all()
    ]
    return create_sales_order(
        customer=order.customer, salesperson=salesperson, items=items,
        shipping_address=order.shipping_address,
    )


# ---------------------------------------------------------------------------
# 18 / 19. 匯入 / 匯出訂單
# ---------------------------------------------------------------------------

def export_sales_orders_csv(queryset):
    import csv
    import io
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(['訂單編號', '客戶', '訂單日期', '狀態', '總金額', '業務人員'])
    for order in queryset:
        writer.writerow([order.so_number, order.customer.customer_name, order.order_date,
                          order.get_status_display(), order.total_amount, order.salesperson])
    return buf.getvalue()


def export_sales_orders_excel(queryset):
    from openpyxl import Workbook
    wb = Workbook()
    ws = wb.active
    ws.title = 'SalesOrders'
    ws.append(['訂單編號', '客戶', '訂單日期', '狀態', '總金額', '業務人員'])
    for order in queryset:
        ws.append([order.so_number, order.customer.customer_name, str(order.order_date),
                   order.get_status_display(), float(order.total_amount), str(order.salesperson)])
    return wb


@transaction.atomic
def import_sales_orders_csv(file_obj, salesperson):
    import csv
    import io
    from inventory.models import Item, Warehouse

    text = file_obj.read().decode('utf-8-sig')
    reader = csv.DictReader(io.StringIO(text))
    created = []
    errors = []
    for row_no, row in enumerate(reader, start=2):
        try:
            customer = Customer.objects.get(customer_code=row['customer_code'])
            item = Item.objects.get(item_code=row['item_code'])
            warehouse = Warehouse.objects.get(warehouse_id=row['warehouse_id'])
            order = create_sales_order(
                customer=customer, salesperson=salesperson,
                items=[{
                    'item': item, 'quantity': Decimal(row['quantity']),
                    'unit_price': Decimal(row['unit_price']), 'warehouse': warehouse,
                }],
            )
            created.append(order)
        except Exception as exc:
            errors.append(f'第 {row_no} 列錯誤：{exc}')
    return {'created': created, 'errors': errors}


# ---------------------------------------------------------------------------
# 20. 銷售儀表板
# ---------------------------------------------------------------------------

def get_sales_dashboard():
    today = timezone.localdate()
    month_start = today.replace(day=1)

    todays_orders = SalesOrder.objects.filter(order_date=today).exclude(status='CANCELLED')
    month_orders = SalesOrder.objects.filter(order_date__gte=month_start).exclude(status='CANCELLED')
    pending_shipment = SalesOrder.objects.filter(status__in=['APPROVED', 'PICKING', 'PACKED'])
    pending_invoice = SalesOrder.objects.filter(status='SHIPPED')
    cancelled_today = SalesOrder.objects.filter(status='CANCELLED', order_date=today)

    top_customers = (
        SalesOrder.objects.exclude(status='CANCELLED')
        .values('customer__customer_code', 'customer__customer_name')
        .annotate(total=Sum('total_amount'))
        .order_by('-total')[:10]
    )
    best_sellers = (
        SalesOrderItem.objects.exclude(sales_order__status='CANCELLED')
        .values('item__item_code', 'item__item_name')
        .annotate(qty=Sum('quantity'))
        .order_by('-qty')[:10]
    )
    total_revenue = month_orders.aggregate(total=Sum('total_amount'))['total'] or Decimal('0')
    order_count = month_orders.count()
    avg_order_amount = (total_revenue / order_count) if order_count else Decimal('0')

    return {
        'todays_order_count': todays_orders.count(),
        'monthly_sales': total_revenue,
        'pending_shipment_count': pending_shipment.count(),
        'pending_invoice_count': pending_invoice.count(),
        'cancelled_today_count': cancelled_today.count(),
        'top_customers': list(top_customers),
        'best_sellers': list(best_sellers),
        'total_revenue': total_revenue,
        'avg_order_amount': avg_order_amount,
    }
