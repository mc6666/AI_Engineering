from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.db.models import F
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, TemplateView, UpdateView, View

from . import services
from .forms import (
    ConfirmSupplierForm, GoodsReceiptForm, PaymentScheduleForm, PurchaseOrderForm,
    PurchaseOrderLineForm, PurchaseRequisitionForm, QuotationForm, RequisitionLineForm, RFQForm,
    SearchPOForm, SupplierForm, SupplierInvoiceForm, SupplierReturnForm, SupplierScorecardForm,
)
from .models import (
    GoodsReceipt, GoodsReceiptItem, PaymentSchedule, PurchaseOrder, PurchaseRequisition, RFQ,
    Supplier, SupplierInvoice,
)


def _flash_validation_error(request, exc):
    messages.error(request, '; '.join(exc.messages))


class IndexView(LoginRequiredMixin, TemplateView):
    template_name = 'purchase/index.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['dashboard'] = services.get_procurement_dashboard()
        return ctx


# ---------------------------------------------------------------------------
# 供應商管理
# ---------------------------------------------------------------------------

class SupplierListView(LoginRequiredMixin, ListView):
    model = Supplier
    template_name = 'purchase/supplier_list.html'
    context_object_name = 'suppliers'


class SupplierCreateView(LoginRequiredMixin, CreateView):
    model = Supplier
    form_class = SupplierForm
    template_name = 'purchase/supplier_form.html'
    success_url = reverse_lazy('purchase:supplier_list')


class SupplierUpdateView(LoginRequiredMixin, UpdateView):
    model = Supplier
    form_class = SupplierForm
    template_name = 'purchase/supplier_form.html'
    success_url = reverse_lazy('purchase:supplier_list')


class SupplierDeleteView(LoginRequiredMixin, DeleteView):
    model = Supplier
    template_name = 'purchase/supplier_confirm_delete.html'
    success_url = reverse_lazy('purchase:supplier_list')


class SupplierScorecardView(LoginRequiredMixin, TemplateView):
    template_name = 'purchase/supplier_scorecard.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        form = SupplierScorecardForm(self.request.GET or None)
        ctx['form'] = form
        if form.is_valid():
            ctx['scorecard'] = services.generate_supplier_scorecard(form.cleaned_data['supplier'])
        return ctx


# ---------------------------------------------------------------------------
# 請購單
# ---------------------------------------------------------------------------

class PurchaseRequisitionListView(LoginRequiredMixin, ListView):
    model = PurchaseRequisition
    template_name = 'purchase/requisition_list.html'
    context_object_name = 'requisitions'
    queryset = PurchaseRequisition.objects.select_related('applicant')


class PurchaseRequisitionCreateView(LoginRequiredMixin, View):
    template_name = 'purchase/requisition_form.html'

    def get(self, request):
        return render(request, self.template_name, {'form': PurchaseRequisitionForm()})

    def post(self, request):
        form = PurchaseRequisitionForm(request.POST)
        if form.is_valid():
            d = form.cleaned_data
            try:
                pr = services.create_purchase_requisition(
                    applicant=request.user, budget_code=d['budget_code'], lines=[],
                    department=d['department'], required_date=d['required_date'], reason=d['reason'],
                )
                messages.success(request, f'已建立請購單 {pr.pr_number}，請於明細頁新增商品。')
                return redirect('purchase:requisition_detail', pk=pr.pk)
            except ValidationError as e:
                _flash_validation_error(request, e)
        return render(request, self.template_name, {'form': form})


class PurchaseRequisitionDetailView(LoginRequiredMixin, DetailView):
    model = PurchaseRequisition
    template_name = 'purchase/requisition_detail.html'
    context_object_name = 'requisition'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['lines'] = self.object.lines.select_related('item')
        ctx['line_form'] = RequisitionLineForm()
        return ctx


class RequisitionAddLineView(LoginRequiredMixin, View):
    def post(self, request, pk):
        requisition = get_object_or_404(PurchaseRequisition, pk=pk)
        form = RequisitionLineForm(request.POST)
        if form.is_valid():
            try:
                services.add_requisition_line(requisition, form.cleaned_data['item'], form.cleaned_data['quantity'])
                messages.success(request, '已新增商品明細。')
            except ValidationError as e:
                _flash_validation_error(request, e)
        else:
            messages.error(request, '商品明細資料有誤。')
        return redirect('purchase:requisition_detail', pk=pk)


class RequisitionApproveView(LoginRequiredMixin, View):
    def post(self, request, pk):
        requisition = get_object_or_404(PurchaseRequisition, pk=pk)
        try:
            services.approve_purchase_requisition(requisition, request.user)
            messages.success(request, '請購單已核准，可進行詢價。')
        except ValidationError as e:
            _flash_validation_error(request, e)
        return redirect('purchase:requisition_detail', pk=pk)


class RequisitionRejectView(LoginRequiredMixin, View):
    def post(self, request, pk):
        requisition = get_object_or_404(PurchaseRequisition, pk=pk)
        try:
            services.reject_purchase_requisition(requisition, request.user)
            messages.success(request, '請購單已駁回。')
        except ValidationError as e:
            _flash_validation_error(request, e)
        return redirect('purchase:requisition_detail', pk=pk)


# ---------------------------------------------------------------------------
# 詢價 RFQ
# ---------------------------------------------------------------------------

class RFQListView(LoginRequiredMixin, ListView):
    model = RFQ
    template_name = 'purchase/rfq_list.html'
    context_object_name = 'rfqs'


class RFQCreateView(LoginRequiredMixin, View):
    template_name = 'purchase/rfq_form.html'

    def get(self, request):
        return render(request, self.template_name, {'form': RFQForm()})

    def post(self, request):
        form = RFQForm(request.POST)
        if form.is_valid():
            d = form.cleaned_data
            try:
                rfq = services.create_rfq(
                    supplier_ids=[s.pk for s in d['suppliers']],
                    quote_deadline=d['quote_deadline'], requisition=d['requisition'],
                )
                messages.success(request, f'已建立詢價單 {rfq.rfq_number}。')
                return redirect('purchase:rfq_detail', pk=rfq.pk)
            except ValidationError as e:
                _flash_validation_error(request, e)
        return render(request, self.template_name, {'form': form})


class RFQDetailView(LoginRequiredMixin, DetailView):
    model = RFQ
    template_name = 'purchase/rfq_detail.html'
    context_object_name = 'rfq'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['rfq_suppliers'] = self.object.rfq_suppliers.select_related('supplier')
        ctx['comparison'] = services.compare_quotations(self.object)
        ctx['recommended'] = services.recommend_supplier(self.object)
        ctx['quotation_form'] = QuotationForm(rfq=self.object)
        return ctx


class RFQSendView(LoginRequiredMixin, View):
    def post(self, request, pk):
        rfq = get_object_or_404(RFQ, pk=pk)
        services.send_rfq(rfq)
        messages.success(request, '詢價單已發送。')
        return redirect('purchase:rfq_detail', pk=pk)


class QuotationCreateView(LoginRequiredMixin, View):
    def post(self, request, pk):
        rfq = get_object_or_404(RFQ, pk=pk)
        form = QuotationForm(request.POST, rfq=rfq)
        if form.is_valid():
            d = form.cleaned_data
            services.record_quotation(
                rfq=rfq, supplier=d['supplier'], item=d['item'], unit_price=d['unit_price'],
                lead_time_days=d['lead_time_days'], payment_terms=d['payment_terms'],
                warranty=d['warranty'], freight=d['freight'],
            )
            messages.success(request, '已登錄供應商報價。')
        else:
            messages.error(request, '報價資料有誤。')
        return redirect('purchase:rfq_detail', pk=pk)


# ---------------------------------------------------------------------------
# 採購訂單
# ---------------------------------------------------------------------------

class PurchaseOrderListView(LoginRequiredMixin, TemplateView):
    template_name = 'purchase/order_list.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        form = SearchPOForm(self.request.GET or None)
        ctx['form'] = form
        filters = {}
        if form.is_valid():
            d = form.cleaned_data
            filters = {
                'po_number': d['po_number'] or None, 'supplier': d['supplier'] or None,
                'buyer': d['buyer'] or None, 'status': d['status'] or None,
                'date_from': d['date_from'], 'date_to': d['date_to'],
            }
        ctx['orders'] = services.search_purchase_orders(**filters)
        return ctx


class PurchaseOrderCreateView(LoginRequiredMixin, View):
    template_name = 'purchase/order_form.html'

    def get(self, request):
        return render(request, self.template_name, {'form': PurchaseOrderForm()})

    def post(self, request):
        form = PurchaseOrderForm(request.POST)
        if form.is_valid():
            d = form.cleaned_data
            try:
                po = services.create_purchase_order(
                    supplier=d['supplier'], buyer=request.user, lines=[],
                    requisition=d['requisition'], required_date=d['required_date'],
                    shipping_address=d['shipping_address'], payment_terms=d['payment_terms'],
                )
                messages.success(request, f'已建立採購訂單 {po.po_number}，請於明細頁新增商品。')
                return redirect('purchase:order_detail', pk=po.pk)
            except ValidationError as e:
                _flash_validation_error(request, e)
        return render(request, self.template_name, {'form': form})


class PurchaseOrderDetailView(LoginRequiredMixin, DetailView):
    model = PurchaseOrder
    template_name = 'purchase/order_detail.html'
    context_object_name = 'po'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['lines'] = self.object.lines.select_related('item', 'warehouse')
        ctx['line_form'] = PurchaseOrderLineForm()
        ctx['confirm_form'] = ConfirmSupplierForm()
        ctx['track'] = services.track_purchase_order(self.object)
        ctx['goods_receipts'] = self.object.goods_receipts.select_related('warehouse')
        ctx['invoices'] = self.object.invoices.all()
        ctx['approval_threshold'] = services.PO_APPROVAL_THRESHOLD
        return ctx


class POAddLineView(LoginRequiredMixin, View):
    def post(self, request, pk):
        po = get_object_or_404(PurchaseOrder, pk=pk)
        form = PurchaseOrderLineForm(request.POST)
        if form.is_valid():
            d = form.cleaned_data
            try:
                services.add_purchase_order_line(
                    po, item=d['item'], quantity=d['quantity'], unit_price=d['unit_price'],
                    warehouse=d['warehouse'], description=d['description'], discount=d['discount'] or 0,
                )
                messages.success(request, '已新增採購明細。')
            except ValidationError as e:
                _flash_validation_error(request, e)
        else:
            messages.error(request, '採購明細資料有誤。')
        return redirect('purchase:order_detail', pk=pk)


class POSubmitView(LoginRequiredMixin, View):
    def post(self, request, pk):
        po = get_object_or_404(PurchaseOrder, pk=pk)
        try:
            services.submit_purchase_order(po)
            messages.success(request, '採購訂單已送審。')
        except ValidationError as e:
            _flash_validation_error(request, e)
        return redirect('purchase:order_detail', pk=pk)


class POApproveView(LoginRequiredMixin, View):
    def post(self, request, pk):
        po = get_object_or_404(PurchaseOrder, pk=pk)
        try:
            services.approve_purchase_order(po, approver=request.user)
            messages.success(request, '採購訂單已核准。')
        except ValidationError as e:
            _flash_validation_error(request, e)
        return redirect('purchase:order_detail', pk=pk)


class POSendView(LoginRequiredMixin, View):
    def post(self, request, pk):
        po = get_object_or_404(PurchaseOrder, pk=pk)
        try:
            services.send_purchase_order(po)
            messages.success(request, '採購訂單已發送給供應商。')
        except ValidationError as e:
            _flash_validation_error(request, e)
        return redirect('purchase:order_detail', pk=pk)


class POConfirmSupplierView(LoginRequiredMixin, View):
    def post(self, request, pk):
        po = get_object_or_404(PurchaseOrder, pk=pk)
        form = ConfirmSupplierForm(request.POST)
        if form.is_valid():
            services.confirm_supplier(po, expected_arrival_date=form.cleaned_data['expected_arrival_date'])
            messages.success(request, '已記錄供應商確認。')
        return redirect('purchase:order_detail', pk=pk)


class POCancelView(LoginRequiredMixin, View):
    def post(self, request, pk):
        po = get_object_or_404(PurchaseOrder, pk=pk)
        try:
            services.cancel_purchase_order(po)
            messages.success(request, '採購訂單已取消。')
        except ValidationError as e:
            _flash_validation_error(request, e)
        return redirect('purchase:order_detail', pk=pk)


class POCloseView(LoginRequiredMixin, View):
    def post(self, request, pk):
        po = get_object_or_404(PurchaseOrder, pk=pk)
        try:
            services.close_purchase_order(po)
            messages.success(request, '採購訂單已結案。')
        except ValidationError as e:
            _flash_validation_error(request, e)
        return redirect('purchase:order_detail', pk=pk)


# ---------------------------------------------------------------------------
# 收貨管理 / 品質驗收 / 供應商退貨
# ---------------------------------------------------------------------------

class GoodsReceiptCreateView(LoginRequiredMixin, View):
    template_name = 'purchase/goods_receipt_form.html'

    def get(self, request, pk):
        po = get_object_or_404(PurchaseOrder, pk=pk)
        return render(request, self.template_name, {
            'po': po, 'form': GoodsReceiptForm(),
            'lines': po.lines.select_related('item').filter(received_qty__lt=F('quantity')),
        })

    def post(self, request, pk):
        po = get_object_or_404(PurchaseOrder, pk=pk)
        form = GoodsReceiptForm(request.POST)
        if form.is_valid():
            receipt_lines = []
            for line in po.lines.all():
                val = request.POST.get(f'qty_{line.pk}')
                if val:
                    try:
                        qty = Decimal(val)
                    except InvalidOperation:
                        continue
                    if qty > 0:
                        receipt_lines.append({'po_item': line, 'quantity': qty})
            try:
                grn = services.receive_goods(po, form.cleaned_data['warehouse'], receipt_lines, request.user)
                messages.success(request, f'已建立收貨單 {grn.grn_number}，請進行品質驗收。')
                return redirect('purchase:goods_receipt_detail', pk=grn.pk)
            except ValidationError as e:
                _flash_validation_error(request, e)
        return render(request, self.template_name, {
            'po': po, 'form': form, 'lines': po.lines.select_related('item').filter(received_qty__lt=F('quantity')),
        })


class GoodsReceiptDetailView(LoginRequiredMixin, DetailView):
    model = GoodsReceipt
    queryset = GoodsReceipt.objects.select_related('purchase_order', 'warehouse')
    template_name = 'purchase/goods_receipt_detail.html'
    context_object_name = 'goods_receipt'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['lines'] = self.object.lines.select_related('po_item__item')
        ctx['return_form'] = SupplierReturnForm()
        return ctx


class QualityInspectionView(LoginRequiredMixin, View):
    def post(self, request, pk):
        line = get_object_or_404(GoodsReceiptItem, pk=pk)
        result = request.POST.get('result')
        try:
            services.quality_inspection(line, result, request.user)
            messages.success(request, '已完成品質驗收。')
        except ValidationError as e:
            _flash_validation_error(request, e)
        return redirect('purchase:goods_receipt_detail', pk=line.goods_receipt_id)


class SupplierReturnCreateView(LoginRequiredMixin, View):
    def post(self, request, pk):
        line = get_object_or_404(GoodsReceiptItem, pk=pk)
        form = SupplierReturnForm(request.POST)
        if form.is_valid():
            try:
                supplier = line.goods_receipt.purchase_order.supplier
                services.return_to_supplier(line, form.cleaned_data['reason'], form.cleaned_data['quantity'], supplier)
                messages.success(request, '已建立供應商退貨單。')
            except ValidationError as e:
                _flash_validation_error(request, e)
        else:
            messages.error(request, '退貨資料有誤。')
        return redirect('purchase:goods_receipt_detail', pk=line.goods_receipt_id)


# ---------------------------------------------------------------------------
# 供應商發票 / 三方比對 / 付款排程
# ---------------------------------------------------------------------------

class SupplierInvoiceCreateView(LoginRequiredMixin, View):
    template_name = 'purchase/invoice_form.html'

    def get(self, request, pk):
        po = get_object_or_404(PurchaseOrder, pk=pk)
        return render(request, self.template_name, {'po': po, 'form': SupplierInvoiceForm()})

    def post(self, request, pk):
        po = get_object_or_404(PurchaseOrder, pk=pk)
        form = SupplierInvoiceForm(request.POST)
        if form.is_valid():
            d = form.cleaned_data
            try:
                invoice = services.process_supplier_invoice(
                    po, invoice_number=d['invoice_number'], invoice_date=d['invoice_date'],
                    amount=d['amount'], payment_terms=d['payment_terms'],
                )
                messages.success(request, f'已建立供應商發票 {invoice.invoice_number}。')
                return redirect('purchase:invoice_detail', pk=invoice.pk)
            except ValidationError as e:
                _flash_validation_error(request, e)
        return render(request, self.template_name, {'po': po, 'form': form})


class SupplierInvoiceDetailView(LoginRequiredMixin, DetailView):
    model = SupplierInvoice
    template_name = 'purchase/invoice_detail.html'
    context_object_name = 'invoice'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['payment_form'] = PaymentScheduleForm()
        ctx['payment_schedules'] = self.object.payment_schedules.all()
        return ctx


class ThreeWayMatchView(LoginRequiredMixin, View):
    def post(self, request, pk):
        invoice = get_object_or_404(SupplierInvoice, pk=pk)
        result = services.three_way_match(invoice.purchase_order, invoice)
        if result['matched']:
            messages.success(request, '三方比對一致（Match）。')
        else:
            messages.warning(request, '三方比對發現差異（Exception）。')
        return redirect('purchase:invoice_detail', pk=pk)


class SchedulePaymentView(LoginRequiredMixin, View):
    def post(self, request, pk):
        invoice = get_object_or_404(SupplierInvoice, pk=pk)
        form = PaymentScheduleForm(request.POST)
        if form.is_valid():
            try:
                services.schedule_payment(invoice, form.cleaned_data['due_date'], form.cleaned_data['early_discount'] or 0)
                messages.success(request, '已安排付款排程。')
            except ValidationError as e:
                _flash_validation_error(request, e)
        else:
            messages.error(request, '付款排程資料有誤。')
        return redirect('purchase:invoice_detail', pk=pk)


class MarkPaymentPaidView(LoginRequiredMixin, View):
    def post(self, request, pk):
        payment = get_object_or_404(PaymentSchedule, pk=pk)
        services.mark_payment_paid(payment)
        messages.success(request, '已標記為已付款。')
        return redirect('purchase:invoice_detail', pk=payment.invoice_id)


# ---------------------------------------------------------------------------
# 補貨建議（重用 inventory）
# ---------------------------------------------------------------------------

class ReorderSuggestionView(LoginRequiredMixin, TemplateView):
    template_name = 'purchase/reorder_suggestions.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['suggestions'] = services.generate_reorder_suggestion()
        return ctx
