from django.conf import settings
from django.db import models
from django.utils import timezone


class ItemCategory(models.Model):
    code = models.CharField(max_length=30, unique=True)
    name = models.CharField(max_length=100)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'item categories'

    def __str__(self):
        return self.name


class Item(models.Model):
    COST_METHOD_CHOICES = [
        ('FIFO', 'FIFO 先進先出'),
        ('LIFO', 'LIFO 後進先出'),
        ('WEIGHTED_AVG', '加權平均法'),
        ('STANDARD', '標準成本法'),
        ('MOVING_AVG', '移動平均法'),
    ]

    item_code = models.CharField(max_length=30, unique=True)
    item_name = models.CharField(max_length=200)
    category = models.ForeignKey(ItemCategory, on_delete=models.PROTECT, related_name='items', null=True, blank=True)
    unit_of_measure = models.CharField(max_length=20, default='EA')
    barcode = models.CharField(max_length=64, blank=True, db_index=True)
    track_lot = models.BooleanField(default=False)
    track_serial = models.BooleanField(default=False)
    standard_cost = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    average_cost = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    costing_method = models.CharField(max_length=20, choices=COST_METHOD_CHOICES, default='WEIGHTED_AVG')
    reorder_point = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    safety_stock = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    lead_time_days = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['item_code']

    def __str__(self):
        return f'{self.item_code} {self.item_name}'


class Warehouse(models.Model):
    warehouse_id = models.CharField(max_length=20, unique=True)
    warehouse_name = models.CharField(max_length=100)
    location = models.CharField(max_length=200, blank=True)
    is_active = models.BooleanField(default=True)
    is_frozen = models.BooleanField(default=False)

    class Meta:
        ordering = ['warehouse_id']

    def __str__(self):
        return f'{self.warehouse_id} {self.warehouse_name}'


class Bin(models.Model):
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='bins')
    bin_code = models.CharField(max_length=30)
    zone = models.CharField(max_length=30, blank=True)
    capacity = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)

    class Meta:
        unique_together = [('warehouse', 'bin_code')]
        ordering = ['warehouse', 'bin_code']

    def __str__(self):
        return f'{self.warehouse.warehouse_id}-{self.bin_code}'


class Lot(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='lots')
    lot_number = models.CharField(max_length=50)
    manufacture_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    supplier_name = models.CharField(max_length=100, blank=True)
    quantity = models.DecimalField(max_digits=14, decimal_places=2, default=0)

    class Meta:
        unique_together = [('item', 'lot_number')]
        ordering = ['expiry_date']

    def __str__(self):
        return f'{self.item.item_code}-{self.lot_number}'

    @property
    def is_expired(self):
        return bool(self.expiry_date and self.expiry_date < timezone.localdate())


class SerialNumberRecord(models.Model):
    STATUS_CHOICES = [
        ('IN_STOCK', '在庫'),
        ('SHIPPED', '已出貨'),
        ('REPAIR', '維修中'),
        ('SCRAPPED', '已報廢'),
    ]
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='serial_numbers')
    serial_no = models.CharField(max_length=100, unique=True)
    warehouse = models.ForeignKey(Warehouse, on_delete=models.SET_NULL, null=True, blank=True, related_name='serial_numbers')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='IN_STOCK')
    warranty_expiry = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['serial_no']

    def __str__(self):
        return self.serial_no


class StockLevel(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='stock_levels')
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='stock_levels')
    on_hand = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    reserved = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    in_transit = models.DecimalField(max_digits=14, decimal_places=2, default=0)

    class Meta:
        unique_together = [('item', 'warehouse')]

    @property
    def available(self):
        return self.on_hand - self.reserved

    def __str__(self):
        return f'{self.item.item_code}@{self.warehouse.warehouse_id}'


class InventoryTransaction(models.Model):
    TYPE_CHOICES = [
        ('RECEIPT', '入庫'),
        ('ISSUE', '出庫'),
        ('TRANSFER_OUT', '調撥-調出'),
        ('TRANSFER_IN', '調撥-調入'),
        ('ADJUSTMENT', '庫存調整'),
        ('RESERVE', '預留'),
        ('RELEASE', '解除預留'),
        ('CYCLE_COUNT', '循環盤點調整'),
        ('PHYSICAL_COUNT', '全面盤點調整'),
    ]
    transaction_no = models.CharField(max_length=30, unique=True)
    transaction_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    item = models.ForeignKey(Item, on_delete=models.PROTECT, related_name='transactions')
    warehouse = models.ForeignKey(Warehouse, on_delete=models.PROTECT, related_name='transactions')
    bin = models.ForeignKey(Bin, on_delete=models.SET_NULL, null=True, blank=True, related_name='transactions')
    lot = models.ForeignKey(Lot, on_delete=models.SET_NULL, null=True, blank=True, related_name='transactions')
    serial_number = models.ForeignKey(SerialNumberRecord, on_delete=models.SET_NULL, null=True, blank=True, related_name='transactions')
    quantity = models.DecimalField(max_digits=14, decimal_places=2)
    unit_cost = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    transaction_date = models.DateTimeField(default=timezone.now)
    reference_document = models.CharField(max_length=50, blank=True)
    reason = models.CharField(max_length=200, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='inventory_transactions')

    class Meta:
        ordering = ['-transaction_date', '-id']

    def __str__(self):
        return self.transaction_no


class InventoryAdjustmentRequest(models.Model):
    STATUS_CHOICES = [('PENDING', '待核准'), ('APPROVED', '已核准'), ('REJECTED', '已駁回')]
    item = models.ForeignKey(Item, on_delete=models.PROTECT, related_name='adjustment_requests')
    warehouse = models.ForeignKey(Warehouse, on_delete=models.PROTECT, related_name='adjustment_requests')
    quantity_delta = models.DecimalField(max_digits=14, decimal_places=2)
    reason = models.CharField(max_length=200)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    requested_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='+')
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    created_at = models.DateTimeField(auto_now_add=True)
    decided_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'ADJ-{self.pk} {self.item.item_code} {self.quantity_delta}'


class CycleCount(models.Model):
    STATUS_CHOICES = [
        ('DRAFT', '草稿'),
        ('COUNTED', '已輸入實盤'),
        ('PENDING_APPROVAL', '待核准'),
        ('APPROVED', '已核准'),
        ('REJECTED', '已駁回'),
    ]
    METHOD_CHOICES = [
        ('ABC', 'ABC分類'),
        ('RANDOM', '隨機抽盤'),
        ('HIGH_VALUE', '高價值商品'),
        ('NEAR_EXPIRY', '即將過期商品'),
    ]
    count_no = models.CharField(max_length=30, unique=True)
    warehouse = models.ForeignKey(Warehouse, on_delete=models.PROTECT, related_name='cycle_counts')
    method = models.CharField(max_length=30, choices=METHOD_CHOICES, default='RANDOM')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='+')
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.count_no


class CycleCountLine(models.Model):
    cycle_count = models.ForeignKey(CycleCount, on_delete=models.CASCADE, related_name='lines')
    item = models.ForeignKey(Item, on_delete=models.PROTECT, related_name='+')
    system_qty = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    counted_qty = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)

    @property
    def variance(self):
        if self.counted_qty is None:
            return None
        return self.counted_qty - self.system_qty


class PhysicalInventory(models.Model):
    STATUS_CHOICES = [
        ('FROZEN', '盤點中(已凍結)'),
        ('COUNTED', '已輸入實盤'),
        ('PENDING_APPROVAL', '待核准'),
        ('APPROVED', '已核准'),
        ('CLOSED', '已結案'),
    ]
    count_no = models.CharField(max_length=30, unique=True)
    warehouse = models.ForeignKey(Warehouse, on_delete=models.PROTECT, related_name='physical_inventories')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='FROZEN')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='+')
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.count_no


class PhysicalInventoryLine(models.Model):
    physical_inventory = models.ForeignKey(PhysicalInventory, on_delete=models.CASCADE, related_name='lines')
    item = models.ForeignKey(Item, on_delete=models.PROTECT, related_name='+')
    system_qty = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    counted_qty = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)

    @property
    def variance(self):
        if self.counted_qty is None:
            return None
        return self.counted_qty - self.system_qty
