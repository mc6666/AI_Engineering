from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, TemplateView, View

from . import services
from .forms import (
    CustomerForm, ImportCSVForm, PaymentForm, SalesOrderHeaderForm, SalesOrderItemFormSet,
    SearchForm, ShipmentForm,
)
from .models import ARInvoice, Customer, SalesOrder


def _flash_validation_error(request, exc):
    messages.error(request, '; '.join(exc.messages))


class IndexView(LoginRequiredMixin, TemplateView):
    template_name = 'sales/index.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['dashboard'] = services.get_sales_dashboard()
        return ctx


# ---------------------------------------------------------------------------
# 客戶管理
# ---------------------------------------------------------------------------

class CustomerListView(LoginRequiredMixin, ListView):
    model = Customer
    template_name = 'sales/customer_list.html'
    context_object_name = 'customers'


class CustomerCreateView(LoginRequiredMixin, CreateView):
    model = Customer
    form_class = CustomerForm
    template_name = 'sales/customer_form.html'
    success_url = reverse_lazy('sales:customer_list')


# ---------------------------------------------------------------------------
# 銷售訂單：查詢 / 建立 / 明細
# ---------------------------------------------------------------------------

class SalesOrderListView(LoginRequiredMixin, ListView):
    template_name = 'sales/order_list.html'
    context_object_name = 'orders'
    paginate_by = 50

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['form'] = SearchForm(self.request.GET or None)
        return ctx

    def get_queryset(self):
        form = SearchForm(self.request.GET or None)
        filters = {}
        if form.is_valid():
            d = form.cleaned_data
            filters = {
                'customer': d['customer'] or None, 'so_number': d['so_number'] or None,
                'status': d['status'] or None, 'date_from': d['date_from'], 'date_to': d['date_to'],
            }
        return services.search_sales_orders(**filters)


class SalesOrderCreateView(LoginRequiredMixin, View):
    template_name = 'sales/order_form.html'

    def get(self, request):
        return render(request, self.template_name, {
            'form': SalesOrderHeaderForm(), 'formset': SalesOrderItemFormSet(),
        })

    def post(self, request):
        form = SalesOrderHeaderForm(request.POST)
        formset = SalesOrderItemFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            items = []
            for item_form in formset:
                if not item_form.cleaned_data or item_form.cleaned_data.get('DELETE'):
                    continue
                d = item_form.cleaned_data
                items.append({
                    'item': d['item'], 'warehouse': d['warehouse'], 'quantity': d['quantity'],
                    'unit_price': d['unit_price'], 'discount': d.get('discount') or 0,
                })
            try:
                order = services.create_sales_order(
                    customer=form.cleaned_data['customer'], salesperson=request.user, items=items,
                    order_date=form.cleaned_data['order_date'], required_date=form.cleaned_data['required_date'],
                    shipping_address=form.cleaned_data['shipping_address'],
                )
                order.discount = form.cleaned_data['discount'] or 0
                order.freight = form.cleaned_data['freight'] or 0
                order.save(update_fields=['discount', 'freight'])
                services.calculate_pricing(order)
                messages.success(request, f'已建立銷售訂單 {order.so_number}。')
                return redirect('sales:order_detail', pk=order.pk)
            except ValidationError as e:
                _flash_validation_error(request, e)
        return render(request, self.template_name, {'form': form, 'formset': formset})


class SalesOrderDetailView(LoginRequiredMixin, DetailView):
    model = SalesOrder
    template_name = 'sales/order_detail.html'
    context_object_name = 'order'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['tax'] = services.calculate_tax(self.object)
        ctx['credit'] = services.check_customer_credit(self.object.customer)
        return ctx


class SalesOrderActionView(LoginRequiredMixin, View):
    action_name = None

    def post(self, request, pk):
        order = get_object_or_404(SalesOrder, pk=pk)
        try:
            self.run_action(request, order)
        except ValidationError as e:
            _flash_validation_error(request, e)
        return redirect('sales:order_detail', pk=pk)

    def run_action(self, request, order):
        raise NotImplementedError


class SubmitOrderView(SalesOrderActionView):
    def run_action(self, request, order):
        allow_backorder = request.POST.get('allow_backorder') == 'on'
        services.submit_order(order, allow_backorder=allow_backorder)
        messages.success(request, '訂單已送出。')


class ApproveOrderView(SalesOrderActionView):
    def run_action(self, request, order):
        services.approve_order(order, approver=request.user)
        messages.success(request, '訂單已核准並預留庫存。')


class CancelOrderView(SalesOrderActionView):
    def run_action(self, request, order):
        services.cancel_order(order, request.user)
        messages.success(request, '訂單已取消，庫存預留已釋放。')


class CloseOrderView(SalesOrderActionView):
    def run_action(self, request, order):
        services.close_order(order)
        messages.success(request, '訂單已結案。')


class GeneratePickingListView(SalesOrderActionView):
    def run_action(self, request, order):
        services.generate_picking_list(order, request.user)
        messages.success(request, '已產生揀貨單。')


class CreateInvoiceView(SalesOrderActionView):
    def run_action(self, request, order):
        services.create_invoice(order)
        messages.success(request, '已開立發票。')


class DuplicateOrderView(LoginRequiredMixin, View):
    def post(self, request, pk):
        order = get_object_or_404(SalesOrder, pk=pk)
        new_order = services.duplicate_order(order, request.user)
        messages.success(request, f'已複製為新訂單 {new_order.so_number}。')
        return redirect('sales:order_detail', pk=new_order.pk)


class CreateShipmentView(LoginRequiredMixin, View):
    template_name = 'sales/shipment_form.html'

    def get(self, request, pk):
        order = get_object_or_404(SalesOrder, pk=pk)
        return render(request, self.template_name, {'form': ShipmentForm(), 'order': order})

    def post(self, request, pk):
        order = get_object_or_404(SalesOrder, pk=pk)
        form = ShipmentForm(request.POST)
        if form.is_valid():
            try:
                services.create_shipment(
                    order, request.user, tracking_number=form.cleaned_data['tracking_number'],
                    carrier=form.cleaned_data['carrier'], ship_date=form.cleaned_data['ship_date'],
                )
                messages.success(request, '已出貨。')
                return redirect('sales:order_detail', pk=pk)
            except ValidationError as e:
                _flash_validation_error(request, e)
        return render(request, self.template_name, {'form': form, 'order': order})


class RecordPaymentView(LoginRequiredMixin, View):
    template_name = 'sales/payment_form.html'

    def get(self, request, pk):
        invoice = get_object_or_404(ARInvoice, pk=pk)
        return render(request, self.template_name, {'form': PaymentForm(), 'invoice': invoice})

    def post(self, request, pk):
        invoice = get_object_or_404(ARInvoice, pk=pk)
        form = PaymentForm(request.POST)
        if form.is_valid():
            try:
                services.record_payment(invoice, form.cleaned_data['amount'])
                messages.success(request, '已登記收款。')
                return redirect('sales:order_detail', pk=invoice.sales_order_id)
            except ValidationError as e:
                _flash_validation_error(request, e)
        return render(request, self.template_name, {'form': form, 'invoice': invoice})


# ---------------------------------------------------------------------------
# 匯入 / 匯出
# ---------------------------------------------------------------------------

class ExportCSVView(LoginRequiredMixin, View):
    def get(self, request):
        content = services.export_sales_orders_csv(services.search_sales_orders())
        response = HttpResponse(content, content_type='text/csv; charset=utf-8-sig')
        response['Content-Disposition'] = 'attachment; filename="sales_orders.csv"'
        return response


class ExportExcelView(LoginRequiredMixin, View):
    def get(self, request):
        wb = services.export_sales_orders_excel(services.search_sales_orders())
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="sales_orders.xlsx"'
        wb.save(response)
        return response


class ExportPDFView(LoginRequiredMixin, TemplateView):
    template_name = 'sales/export_print.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['orders'] = services.search_sales_orders()
        return ctx


class ImportCSVView(LoginRequiredMixin, View):
    template_name = 'sales/import_form.html'

    def get(self, request):
        return render(request, self.template_name, {'form': ImportCSVForm()})

    def post(self, request):
        form = ImportCSVForm(request.POST, request.FILES)
        if form.is_valid():
            result = services.import_sales_orders_csv(form.cleaned_data['file'], request.user)
            messages.success(request, f'成功匯入 {len(result["created"])} 筆訂單。')
            for err in result['errors']:
                messages.error(request, err)
            return redirect('sales:order_list')
        return render(request, self.template_name, {'form': form})
