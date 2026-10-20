from decimal import Decimal

from django.conf import settings
from django.db import models

from inventory.models import Item, Warehouse


class Supplier(models.Model):
    supplier_id = models.CharField(max_length=20, unique=True)
    supplier_name = models.CharField(max_length=150)
    payment_terms = models.CharField(max_length=100, blank=True)
    credit_limit = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    contact_person = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True)
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['supplier_id']

    def __str__(self):
        return f'{self.supplier_id} {self.supplier_name}'


class PurchaseRequisition(models.Model):
    STATUS_CHOICES = [('DRAFT', '草稿'), ('APPROVED', '已核准'), ('REJECTED', '已駁回')]
    pr_number = models.CharField(max_length=30, unique=True)
    applicant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='+')
    department = models.CharField(max_length=100, blank=True)
    required_date = models.DateField(null=True, blank=True)
    budget_code = models.CharField(max_length=50)
    reason = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.pr_number


class PurchaseRequisitionItem(models.Model):
    requisition = models.ForeignKey(PurchaseRequisition, on_delete=models.CASCADE, related_name='lines')
    item = models.ForeignKey(Item, on_delete=models.PROTECT, related_name='+')
    quantity = models.DecimalField(max_digits=14, decimal_places=2)

    def __str__(self):
        return f'{self.requisition.pr_number}-{self.item.item_code}'


class RFQ(models.Model):
    STATUS_CHOICES = [('DRAFT', '草稿'), ('SENT', '已發送'), ('CLOSED', '已結束')]
    rfq_number = models.CharField(max_length=30, unique=True)
    requisition = models.ForeignKey(PurchaseRequisition, on_delete=models.SET_NULL, null=True, blank=True, related_name='rfqs')
    quote_deadline = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    suppliers = models.ManyToManyField(Supplier, through='RFQSupplier', related_name='rfqs')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.rfq_number


class RFQSupplier(models.Model):
    rfq = models.ForeignKey(RFQ, on_delete=models.CASCADE, related_name='rfq_suppliers')
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='+')
    sent_at = models.DateTimeField(null=True, blank=True)
    replied = models.BooleanField(default=False)

    class Meta:
        unique_together = [('rfq', 'supplier')]

    def __str__(self):
        return f'{self.rfq.rfq_number}-{self.supplier.supplier_id}'


class Quotation(models.Model):
    rfq = models.ForeignKey(RFQ, on_delete=models.CASCADE, related_name='quotations')
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='quotations')
    item = models.ForeignKey(Item, on_delete=models.PROTECT, related_name='+')
    unit_price = models.DecimalField(max_digits=14, decimal_places=4)
    lead_time_days = models.PositiveIntegerField(default=0)
    payment_terms = models.CharField(max_length=100, blank=True)
    warranty = models.CharField(max_length=100, blank=True)
    freight = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.rfq.rfq_number}-{self.supplier.supplier_id}-{self.item.item_code}'


class PurchaseOrder(models.Model):
    STATUS_CHOICES = [
        ('DRAFT', '草稿'), ('SUBMITTED', '已送審'), ('APPROVED', '已核准'), ('SENT', '已送出'),
        ('PARTIALLY_RECEIVED', '部分收貨'), ('RECEIVED', '已收貨'), ('INVOICED', '已開立發票'),
        ('CLOSED', '已結案'), ('CANCELLED', '已取消'),
    ]
    po_number = models.CharField(max_length=30, unique=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT, related_name='purchase_orders')
    requisition = models.ForeignKey(PurchaseRequisition, on_delete=models.SET_NULL, null=True, blank=True, related_name='purchase_orders')
    order_date = models.DateField(auto_now_add=True)
    required_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    shipping_address = models.CharField(max_length=255, blank=True)
    payment_terms = models.CharField(max_length=100, blank=True)
    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='+')
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    sent_at = models.DateTimeField(null=True, blank=True)
    supplier_confirmed = models.BooleanField(default=False)
    expected_arrival_date = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ['-order_date', '-id']

    def __str__(self):
        return self.po_number

    @property
    def total_amount(self):
        return sum((line.line_total for line in self.lines.all()), Decimal('0'))


class PurchaseOrderItem(models.Model):
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name='lines')
    item = models.ForeignKey(Item, on_delete=models.PROTECT, related_name='+')
    description = models.CharField(max_length=255, blank=True)
    quantity = models.DecimalField(max_digits=14, decimal_places=2)
    unit_price = models.DecimalField(max_digits=14, decimal_places=4)
    discount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    warehouse = models.ForeignKey(Warehouse, on_delete=models.PROTECT, related_name='+')
    received_qty = models.DecimalField(max_digits=14, decimal_places=2, default=0)

    def __str__(self):
        return f'{self.purchase_order.po_number}-{self.item.item_code}'

    @property
    def remaining_qty(self):
        return self.quantity - self.received_qty

    @property
    def line_total(self):
        return (self.quantity * self.unit_price) - self.discount


class GoodsReceipt(models.Model):
    grn_number = models.CharField(max_length=30, unique=True)
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.PROTECT, related_name='goods_receipts')
    warehouse = models.ForeignKey(Warehouse, on_delete=models.PROTECT, related_name='+')
    received_date = models.DateTimeField(auto_now_add=True)
    received_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='+')

    class Meta:
        ordering = ['-received_date']

    def __str__(self):
        return self.grn_number


class GoodsReceiptItem(models.Model):
    QUALITY_CHOICES = [('PENDING', '待驗'), ('PASS', '合格'), ('FAIL', '不合格'), ('RETURN', '退貨')]
    goods_receipt = models.ForeignKey(GoodsReceipt, on_delete=models.CASCADE, related_name='lines')
    po_item = models.ForeignKey(PurchaseOrderItem, on_delete=models.PROTECT, related_name='receipt_lines')
    received_qty = models.DecimalField(max_digits=14, decimal_places=2)
    quality_result = models.CharField(max_length=20, choices=QUALITY_CHOICES, default='PENDING')

    def __str__(self):
        return f'{self.goods_receipt.grn_number}-{self.po_item.item.item_code}'


class SupplierReturn(models.Model):
    REASON_CHOICES = [
        ('DAMAGED', '商品損壞'), ('WRONG_ITEM', '商品錯誤'), ('QUALITY', '品質不符'), ('OVER_SHIPMENT', '超量交貨'),
    ]
    return_no = models.CharField(max_length=30, unique=True)
    goods_receipt_item = models.ForeignKey(GoodsReceiptItem, on_delete=models.PROTECT, related_name='returns')
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT, related_name='returns')
    reason = models.CharField(max_length=20, choices=REASON_CHOICES)
    quantity = models.DecimalField(max_digits=14, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.return_no


class SupplierInvoice(models.Model):
    MATCH_CHOICES = [('PENDING', '待比對'), ('MATCHED', '一致'), ('EXCEPTION', '差異')]
    invoice_number = models.CharField(max_length=30, unique=True)
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.PROTECT, related_name='invoices')
    invoice_date = models.DateField()
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    payment_terms = models.CharField(max_length=100, blank=True)
    match_status = models.CharField(max_length=20, choices=MATCH_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.invoice_number


class PaymentSchedule(models.Model):
    STATUS_CHOICES = [('SCHEDULED', '已排程'), ('PAID', '已付款')]
    invoice = models.ForeignKey(SupplierInvoice, on_delete=models.CASCADE, related_name='payment_schedules')
    due_date = models.DateField()
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    early_discount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='SCHEDULED')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['due_date']

    def __str__(self):
        return f'PAY-{self.pk}'
