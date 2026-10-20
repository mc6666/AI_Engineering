from django import forms

from inventory.models import Item, Warehouse

from .models import ARInvoice, Customer, SalesOrder, Shipment


class BootstrapFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if isinstance(field.widget, (forms.CheckboxInput,)):
                field.widget.attrs.setdefault('class', 'form-check-input')
            else:
                field.widget.attrs.setdefault('class', 'form-control')


class CustomerForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['customer_code', 'customer_name', 'credit_limit', 'payment_terms', 'shipping_address', 'is_active']


class SalesOrderHeaderForm(BootstrapFormMixin, forms.Form):
    customer = forms.ModelChoiceField(queryset=Customer.objects.filter(is_active=True))
    order_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    required_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    shipping_address = forms.CharField(required=False, max_length=255)
    discount = forms.DecimalField(required=False, initial=0, min_value=0)
    freight = forms.DecimalField(required=False, initial=0, min_value=0)
    allow_backorder = forms.BooleanField(required=False, help_text='允許超出可用庫存的缺貨接單')


class SalesOrderItemForm(BootstrapFormMixin, forms.Form):
    item = forms.ModelChoiceField(queryset=Item.objects.filter(is_active=True))
    warehouse = forms.ModelChoiceField(queryset=Warehouse.objects.filter(is_active=True))
    quantity = forms.DecimalField(min_value=0.0001)
    unit_price = forms.DecimalField(min_value=0)
    discount = forms.DecimalField(required=False, initial=0, min_value=0)


SalesOrderItemFormSet = forms.formset_factory(SalesOrderItemForm, extra=1, can_delete=True)


class ShipmentForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Shipment
        fields = ['tracking_number', 'carrier', 'ship_date']
        widgets = {'ship_date': forms.DateInput(attrs={'type': 'date'})}


class PaymentForm(BootstrapFormMixin, forms.Form):
    amount = forms.DecimalField(min_value=0.01)


class SearchForm(BootstrapFormMixin, forms.Form):
    customer = forms.ModelChoiceField(queryset=Customer.objects.all(), required=False)
    so_number = forms.CharField(required=False, max_length=30)
    status = forms.ChoiceField(choices=[('', '全部')] + SalesOrder.STATUS_CHOICES, required=False)
    date_from = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    date_to = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))


class ImportCSVForm(BootstrapFormMixin, forms.Form):
    file = forms.FileField(help_text='CSV 欄位需包含 customer_code, item_code, warehouse_id, quantity, unit_price')
