from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils import timezone

from inventory.models import Item, Warehouse


class Customer(models.Model):
    customer_code = models.CharField(max_length=30, unique=True)
    customer_name = models.CharField(max_length=200)
    credit_limit = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    outstanding_balance = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    payment_terms = models.CharField(max_length=100, blank=True)
    shipping_address = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['customer_code']

    def __str__(self):
        return f'{self.customer_code} {self.customer_name}'

    @property
    def available_credit(self):
        return self.credit_limit - self.outstanding_balance


class SalesOrder(models.Model):
    STATUS_CHOICES = [
        ('DRAFT', '草稿'),
        ('OPEN', '已開立'),
        ('APPROVED', '已核准'),
        ('PICKING', '揀貨中'),
        ('PACKED', '包裝中'),
        ('SHIPPED', '已出貨'),
        ('INVOICED', '已開立發票'),
        ('CLOSED', '已結案'),
        ('CANCELLED', '已取消'),
    ]
    so_number = models.CharField(max_length=30, unique=True)
    order_date = models.DateField(default=timezone.localdate)
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name='sales_orders')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    total_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    freight = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    salesperson = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='sales_orders')
    required_date = models.DateField(null=True, blank=True)
    shipping_address = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.so_number

    @property
    def subtotal(self):
        return sum((line.line_total for line in self.items.all()), Decimal('0'))


class SalesOrderItem(models.Model):
    sales_order = models.ForeignKey(SalesOrder, on_delete=models.CASCADE, related_name='items')
    item = models.ForeignKey(Item, on_delete=models.PROTECT, related_name='+')
    description = models.CharField(max_length=200, blank=True)
    quantity = models.DecimalField(max_digits=14, decimal_places=2)
    unit_price = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    discount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    warehouse = models.ForeignKey(Warehouse, on_delete=models.PROTECT, related_name='+')

    def __str__(self):
        return f'{self.sales_order.so_number}-{self.item.item_code}'

    @property
    def line_total(self):
        return (self.quantity * self.unit_price) - self.discount

    @property
    def available_qty(self):
        from inventory.services import search_inventory
        results = search_inventory(item=self.item, warehouse=self.warehouse)
        return results[0]['available'] if results else Decimal('0')


class PickingList(models.Model):
    sales_order = models.OneToOneField(SalesOrder, on_delete=models.CASCADE, related_name='picking_list')
    generated_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='+')

    def __str__(self):
        return f'PICK-{self.sales_order.so_number}'


class PickingListLine(models.Model):
    picking_list = models.ForeignKey(PickingList, on_delete=models.CASCADE, related_name='lines')
    item = models.ForeignKey(Item, on_delete=models.PROTECT, related_name='+')
    warehouse = models.ForeignKey(Warehouse, on_delete=models.PROTECT, related_name='+')
    pick_qty = models.DecimalField(max_digits=14, decimal_places=2)


class Shipment(models.Model):
    sales_order = models.ForeignKey(SalesOrder, on_delete=models.PROTECT, related_name='shipments')
    shipment_no = models.CharField(max_length=30, unique=True)
    tracking_number = models.CharField(max_length=100, blank=True)
    carrier = models.CharField(max_length=100, blank=True)
    ship_date = models.DateField(default=timezone.localdate)

    class Meta:
        ordering = ['-ship_date']

    def __str__(self):
        return self.shipment_no


class ARInvoice(models.Model):
    sales_order = models.ForeignKey(SalesOrder, on_delete=models.PROTECT, related_name='invoices')
    invoice_no = models.CharField(max_length=30, unique=True)
    invoice_date = models.DateField(default=timezone.localdate)
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    paid_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)

    class Meta:
        ordering = ['-invoice_date']

    def __str__(self):
        return self.invoice_no

    @property
    def outstanding(self):
        return self.amount - self.paid_amount
