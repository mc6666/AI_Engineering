from django import forms
from django.contrib.auth import get_user_model

from inventory.models import Item, Warehouse

from .models import (
    PaymentSchedule, PurchaseOrder, PurchaseRequisition, Quotation, RFQ, Supplier, SupplierInvoice,
    SupplierReturn,
)


class BootstrapFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.setdefault('class', 'form-check-input')
            elif isinstance(field.widget, forms.CheckboxSelectMultiple):
                pass
            else:
                field.widget.attrs.setdefault('class', 'form-control')


class SupplierForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ['supplier_id', 'supplier_name', 'payment_terms', 'credit_limit',
                  'contact_person', 'email', 'rating', 'is_active']


class PurchaseRequisitionForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = PurchaseRequisition
        fields = ['department', 'budget_code', 'required_date', 'reason']
        widgets = {'required_date': forms.DateInput(attrs={'type': 'date'})}


class RequisitionLineForm(BootstrapFormMixin, forms.Form):
    item = forms.ModelChoiceField(queryset=Item.objects.filter(is_active=True))
    quantity = forms.DecimalField(min_value=0.0001)


class RFQForm(BootstrapFormMixin, forms.Form):
    requisition = forms.ModelChoiceField(
        queryset=PurchaseRequisition.objects.filter(status='APPROVED'), required=False,
    )
    quote_deadline = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    suppliers = forms.ModelMultipleChoiceField(
        queryset=Supplier.objects.filter(is_active=True), widget=forms.CheckboxSelectMultiple,
    )


class QuotationForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Quotation
        fields = ['supplier', 'item', 'unit_price', 'lead_time_days', 'payment_terms', 'warranty', 'freight']

    def __init__(self, *args, rfq=None, **kwargs):
        super().__init__(*args, **kwargs)
        if rfq is not None:
            self.fields['supplier'].queryset = rfq.suppliers.all()


class PurchaseOrderForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = PurchaseOrder
        fields = ['supplier', 'requisition', 'required_date', 'shipping_address', 'payment_terms']
        widgets = {'required_date': forms.DateInput(attrs={'type': 'date'})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['supplier'].queryset = Supplier.objects.filter(is_active=True)
        self.fields['requisition'].queryset = PurchaseRequisition.objects.filter(status='APPROVED')
        self.fields['requisition'].required = False


class PurchaseOrderLineForm(BootstrapFormMixin, forms.Form):
    item = forms.ModelChoiceField(queryset=Item.objects.filter(is_active=True))
    description = forms.CharField(max_length=255, required=False)
    quantity = forms.DecimalField(min_value=0.0001)
    unit_price = forms.DecimalField(min_value=0)
    discount = forms.DecimalField(min_value=0, required=False, initial=0)
    warehouse = forms.ModelChoiceField(queryset=Warehouse.objects.filter(is_active=True))


class ConfirmSupplierForm(BootstrapFormMixin, forms.Form):
    expected_arrival_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))


class GoodsReceiptForm(BootstrapFormMixin, forms.Form):
    warehouse = forms.ModelChoiceField(queryset=Warehouse.objects.filter(is_active=True))


class SupplierReturnForm(BootstrapFormMixin, forms.Form):
    reason = forms.ChoiceField(choices=SupplierReturn.REASON_CHOICES)
    quantity = forms.DecimalField(min_value=0.0001)


class SupplierInvoiceForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = SupplierInvoice
        fields = ['invoice_number', 'invoice_date', 'amount', 'payment_terms']
        widgets = {'invoice_date': forms.DateInput(attrs={'type': 'date'})}


class PaymentScheduleForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = PaymentSchedule
        fields = ['due_date', 'early_discount']
        widgets = {'due_date': forms.DateInput(attrs={'type': 'date'})}


class SearchPOForm(BootstrapFormMixin, forms.Form):
    po_number = forms.CharField(required=False)
    supplier = forms.ModelChoiceField(queryset=Supplier.objects.all(), required=False)
    buyer = forms.ModelChoiceField(queryset=get_user_model().objects.all(), required=False)
    status = forms.ChoiceField(choices=[('', '全部狀態')] + list(PurchaseOrder.STATUS_CHOICES), required=False)
    date_from = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    date_to = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))


class SupplierScorecardForm(BootstrapFormMixin, forms.Form):
    supplier = forms.ModelChoiceField(queryset=Supplier.objects.all())
