from django import forms

from .models import (
    Bin, InventoryAdjustmentRequest, Item, ItemCategory, Lot, SerialNumberRecord, Warehouse,
)


class BootstrapFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if isinstance(field.widget, (forms.CheckboxInput,)):
                field.widget.attrs.setdefault('class', 'form-check-input')
            else:
                field.widget.attrs.setdefault('class', 'form-control')


class ItemCategoryForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = ItemCategory
        fields = ['code', 'name']


class ItemForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Item
        fields = [
            'item_code', 'item_name', 'category', 'unit_of_measure', 'barcode',
            'track_lot', 'track_serial', 'standard_cost', 'average_cost', 'costing_method',
            'reorder_point', 'safety_stock', 'lead_time_days', 'is_active',
        ]


class WarehouseForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Warehouse
        fields = ['warehouse_id', 'warehouse_name', 'location', 'is_active']


class BinForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Bin
        fields = ['bin_code', 'zone', 'capacity']


class LotForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Lot
        fields = ['item', 'lot_number', 'manufacture_date', 'expiry_date', 'supplier_name', 'quantity']
        widgets = {
            'manufacture_date': forms.DateInput(attrs={'type': 'date'}),
            'expiry_date': forms.DateInput(attrs={'type': 'date'}),
        }


class SerialForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = SerialNumberRecord
        fields = ['item', 'serial_no', 'warehouse', 'status', 'warranty_expiry', 'notes']
        widgets = {'warranty_expiry': forms.DateInput(attrs={'type': 'date'})}


class ReceiveForm(BootstrapFormMixin, forms.Form):
    item = forms.ModelChoiceField(queryset=Item.objects.filter(is_active=True))
    warehouse = forms.ModelChoiceField(queryset=Warehouse.objects.filter(is_active=True))
    bin = forms.ModelChoiceField(queryset=Bin.objects.all(), required=False)
    quantity = forms.DecimalField(min_value=0.0001)
    unit_cost = forms.DecimalField(min_value=0, required=False, initial=0)
    reference_document = forms.CharField(max_length=50, required=False)
    lot_number = forms.CharField(max_length=50, required=False)
    lot_manufacture_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    lot_expiry = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    supplier_name = forms.CharField(max_length=100, required=False)


class IssueForm(BootstrapFormMixin, forms.Form):
    item = forms.ModelChoiceField(queryset=Item.objects.filter(is_active=True))
    warehouse = forms.ModelChoiceField(queryset=Warehouse.objects.filter(is_active=True))
    bin = forms.ModelChoiceField(queryset=Bin.objects.all(), required=False)
    quantity = forms.DecimalField(min_value=0.0001)
    reference_document = forms.CharField(max_length=50, required=False)
    allow_negative = forms.BooleanField(required=False)


class TransferForm(BootstrapFormMixin, forms.Form):
    item = forms.ModelChoiceField(queryset=Item.objects.filter(is_active=True))
    from_warehouse = forms.ModelChoiceField(queryset=Warehouse.objects.filter(is_active=True))
    to_warehouse = forms.ModelChoiceField(queryset=Warehouse.objects.filter(is_active=True))
    quantity = forms.DecimalField(min_value=0.0001)
    reference_document = forms.CharField(max_length=50, required=False)


class ReserveForm(BootstrapFormMixin, forms.Form):
    item = forms.ModelChoiceField(queryset=Item.objects.filter(is_active=True))
    warehouse = forms.ModelChoiceField(queryset=Warehouse.objects.filter(is_active=True))
    quantity = forms.DecimalField(min_value=0.0001)
    reference_document = forms.CharField(max_length=50, required=False)


class ReleaseForm(ReserveForm):
    pass


class AdjustmentRequestForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = InventoryAdjustmentRequest
        fields = ['item', 'warehouse', 'quantity_delta', 'reason']


class CycleCountCreateForm(BootstrapFormMixin, forms.Form):
    warehouse = forms.ModelChoiceField(queryset=Warehouse.objects.filter(is_active=True))
    method = forms.ChoiceField(choices=[
        ('ABC', 'ABC分類'), ('RANDOM', '隨機抽盤'), ('HIGH_VALUE', '高價值商品'), ('NEAR_EXPIRY', '即將過期商品'),
    ])
    item_codes = forms.CharField(
        required=False, help_text='選填，以逗號分隔指定商品代號；留空則依方法自動選取。',
    )
