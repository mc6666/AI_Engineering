from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.db.models import ProtectedError, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, TemplateView, UpdateView, View

from . import services
from .forms import (
    AdjustmentRequestForm, BinForm, CycleCountCreateForm, IssueForm, ItemCategoryForm,
    ItemForm, LotForm, ReceiveForm, ReleaseForm, ReserveForm, SerialForm, TransferForm,
    WarehouseForm,
)
from .models import (
    Bin, CycleCount, InventoryAdjustmentRequest, InventoryTransaction, Item, ItemCategory,
    Lot, PhysicalInventory, SerialNumberRecord, Warehouse,
)


def _flash_validation_error(request, exc):
    messages.error(request, '; '.join(exc.messages))


class IndexView(LoginRequiredMixin, TemplateView):
    template_name = 'inventory/index.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['dashboard'] = services.get_inventory_dashboard()
        return ctx


# ---------------------------------------------------------------------------
# 商品主檔管理
# ---------------------------------------------------------------------------

class ItemListView(LoginRequiredMixin, ListView):
    template_name = 'inventory/item_list.html'
    context_object_name = 'items'
    paginate_by = 50

    def get_queryset(self):
        qs = Item.objects.select_related('category')
        q = self.request.GET.get('q')
        if q:
            qs = qs.filter(Q(item_code__icontains=q) | Q(item_name__icontains=q))
        return qs


class ItemCreateView(LoginRequiredMixin, CreateView):
    model = Item
    form_class = ItemForm
    template_name = 'inventory/item_form.html'
    success_url = reverse_lazy('inventory:item_list')


class ItemUpdateView(LoginRequiredMixin, UpdateView):
    model = Item
    form_class = ItemForm
    template_name = 'inventory/item_form.html'
    success_url = reverse_lazy('inventory:item_list')


class ItemDeleteView(LoginRequiredMixin, DeleteView):
    model = Item
    template_name = 'inventory/item_confirm_delete.html'
    success_url = reverse_lazy('inventory:item_list')

    def form_valid(self, form):
        try:
            return super().form_valid(form)
        except ProtectedError:
            messages.error(self.request, '此商品已有庫存交易紀錄，無法刪除。')
            return redirect('inventory:item_list')


class ItemDetailView(LoginRequiredMixin, DetailView):
    model = Item
    template_name = 'inventory/item_detail.html'
    context_object_name = 'item'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['stock_levels'] = self.object.stock_levels.select_related('warehouse')
        ctx['lots'] = self.object.lots.all()
        ctx['serial_numbers'] = self.object.serial_numbers.all()
        return ctx


class GenerateBarcodeView(LoginRequiredMixin, View):
    def post(self, request, pk):
        item = get_object_or_404(Item, pk=pk)
        services.generate_barcode(item)
        messages.success(request, f'已產生條碼：{item.barcode}')
        return redirect('inventory:item_detail', pk=pk)


class ItemCategoryListView(LoginRequiredMixin, ListView):
    model = ItemCategory
    template_name = 'inventory/category_list.html'
    context_object_name = 'categories'


class ItemCategoryCreateView(LoginRequiredMixin, CreateView):
    model = ItemCategory
    form_class = ItemCategoryForm
    template_name = 'inventory/category_form.html'
    success_url = reverse_lazy('inventory:category_list')


class ItemCategoryDeleteView(LoginRequiredMixin, DeleteView):
    model = ItemCategory
    template_name = 'inventory/category_confirm_delete.html'
    success_url = reverse_lazy('inventory:category_list')


# ---------------------------------------------------------------------------
# 倉庫管理
# ---------------------------------------------------------------------------

class WarehouseListView(LoginRequiredMixin, ListView):
    model = Warehouse
    template_name = 'inventory/warehouse_list.html'
    context_object_name = 'warehouses'


class WarehouseCreateView(LoginRequiredMixin, CreateView):
    model = Warehouse
    form_class = WarehouseForm
    template_name = 'inventory/warehouse_form.html'
    success_url = reverse_lazy('inventory:warehouse_list')


class WarehouseUpdateView(LoginRequiredMixin, UpdateView):
    model = Warehouse
    form_class = WarehouseForm
    template_name = 'inventory/warehouse_form.html'
    success_url = reverse_lazy('inventory:warehouse_list')


class WarehouseDeleteView(LoginRequiredMixin, DeleteView):
    model = Warehouse
    template_name = 'inventory/warehouse_confirm_delete.html'
    success_url = reverse_lazy('inventory:warehouse_list')


class WarehouseDetailView(LoginRequiredMixin, DetailView):
    model = Warehouse
    template_name = 'inventory/warehouse_detail.html'
    context_object_name = 'warehouse'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['bins'] = self.object.bins.all()
        ctx['bin_form'] = BinForm()
        return ctx


class BinCreateView(LoginRequiredMixin, View):
    def post(self, request, warehouse_pk):
        warehouse = get_object_or_404(Warehouse, pk=warehouse_pk)
        form = BinForm(request.POST)
        if form.is_valid():
            services.create_bin(
                warehouse, form.cleaned_data['bin_code'],
                form.cleaned_data['zone'], form.cleaned_data['capacity'],
            )
            messages.success(request, '已新增儲位。')
        else:
            messages.error(request, '儲位資料有誤。')
        return redirect('inventory:warehouse_detail', pk=warehouse_pk)


class BinDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        bin_obj = get_object_or_404(Bin, pk=pk)
        warehouse_pk = bin_obj.warehouse_id
        services.delete_bin(bin_obj)
        return redirect('inventory:warehouse_detail', pk=warehouse_pk)


# ---------------------------------------------------------------------------
# 庫存查詢
# ---------------------------------------------------------------------------

class StockSearchView(LoginRequiredMixin, TemplateView):
    template_name = 'inventory/stock_search.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['items'] = Item.objects.all()
        ctx['warehouses'] = Warehouse.objects.all()
        params = self.request.GET
        if params:
            item = Item.objects.filter(pk=params.get('item')).first() if params.get('item') else None
            warehouse = Warehouse.objects.filter(pk=params.get('warehouse')).first() if params.get('warehouse') else None
            ctx['results'] = services.search_inventory(
                item=item, warehouse=warehouse,
                barcode=params.get('barcode') or None,
                lot_number=params.get('lot_number') or None,
                serial_no=params.get('serial_no') or None,
                bin_code=params.get('bin_code') or None,
            )
        return ctx


# ---------------------------------------------------------------------------
# 入庫 / 出庫 / 調撥 / 預留
# ---------------------------------------------------------------------------

class ReceiveInventoryView(LoginRequiredMixin, View):
    template_name = 'inventory/receive_form.html'

    def get(self, request):
        return render(request, self.template_name, {'form': ReceiveForm()})

    def post(self, request):
        form = ReceiveForm(request.POST)
        if form.is_valid():
            d = form.cleaned_data
            try:
                services.receive_inventory(
                    item=d['item'], warehouse=d['warehouse'], quantity=d['quantity'],
                    unit_cost=d['unit_cost'] or 0, user=request.user,
                    reference_document=d['reference_document'], bin=d['bin'],
                    lot_number=d['lot_number'] or None, lot_expiry=d['lot_expiry'],
                    lot_manufacture_date=d['lot_manufacture_date'], supplier_name=d['supplier_name'],
                )
                messages.success(request, '入庫成功。')
                return redirect('inventory:receive')
            except ValidationError as e:
                _flash_validation_error(request, e)
        return render(request, self.template_name, {'form': form})


class IssueInventoryView(LoginRequiredMixin, View):
    template_name = 'inventory/issue_form.html'

    def get(self, request):
        return render(request, self.template_name, {'form': IssueForm()})

    def post(self, request):
        form = IssueForm(request.POST)
        if form.is_valid():
            d = form.cleaned_data
            try:
                services.issue_inventory(
                    item=d['item'], warehouse=d['warehouse'], quantity=d['quantity'],
                    user=request.user, reference_document=d['reference_document'],
                    bin=d['bin'], allow_negative=d['allow_negative'],
                )
                messages.success(request, '出庫成功。')
                return redirect('inventory:issue')
            except ValidationError as e:
                _flash_validation_error(request, e)
        return render(request, self.template_name, {'form': form})


class TransferInventoryView(LoginRequiredMixin, View):
    template_name = 'inventory/transfer_form.html'

    def get(self, request):
        return render(request, self.template_name, {'form': TransferForm()})

    def post(self, request):
        form = TransferForm(request.POST)
        if form.is_valid():
            d = form.cleaned_data
            try:
                services.transfer_inventory(
                    item=d['item'], from_warehouse=d['from_warehouse'], to_warehouse=d['to_warehouse'],
                    quantity=d['quantity'], user=request.user, reference_document=d['reference_document'],
                )
                messages.success(request, '庫存調撥成功。')
                return redirect('inventory:transfer')
            except ValidationError as e:
                _flash_validation_error(request, e)
        return render(request, self.template_name, {'form': form})


class ReserveInventoryView(LoginRequiredMixin, View):
    template_name = 'inventory/reserve_form.html'

    def get(self, request):
        return render(request, self.template_name, {'form': ReserveForm()})

    def post(self, request):
        form = ReserveForm(request.POST)
        if form.is_valid():
            d = form.cleaned_data
            try:
                services.reserve_inventory(
                    item=d['item'], warehouse=d['warehouse'], quantity=d['quantity'],
                    user=request.user, reference_document=d['reference_document'],
                )
                messages.success(request, '已預留庫存。')
                return redirect('inventory:reserve')
            except ValidationError as e:
                _flash_validation_error(request, e)
        return render(request, self.template_name, {'form': form})


class ReleaseReservationView(LoginRequiredMixin, View):
    template_name = 'inventory/release_form.html'

    def get(self, request):
        return render(request, self.template_name, {'form': ReleaseForm()})

    def post(self, request):
        form = ReleaseForm(request.POST)
        if form.is_valid():
            d = form.cleaned_data
            try:
                services.release_reservation(
                    item=d['item'], warehouse=d['warehouse'], quantity=d['quantity'],
                    user=request.user, reference_document=d['reference_document'],
                )
                messages.success(request, '已解除預留。')
                return redirect('inventory:release')
            except ValidationError as e:
                _flash_validation_error(request, e)
        return render(request, self.template_name, {'form': form})


# ---------------------------------------------------------------------------
# 庫存調整
# ---------------------------------------------------------------------------

class AdjustmentRequestListView(LoginRequiredMixin, ListView):
    model = InventoryAdjustmentRequest
    template_name = 'inventory/adjustment_list.html'
    context_object_name = 'adjustments'
    queryset = InventoryAdjustmentRequest.objects.select_related('item', 'warehouse', 'requested_by')


class AdjustmentRequestCreateView(LoginRequiredMixin, View):
    template_name = 'inventory/adjustment_form.html'

    def get(self, request):
        return render(request, self.template_name, {'form': AdjustmentRequestForm()})

    def post(self, request):
        form = AdjustmentRequestForm(request.POST)
        if form.is_valid():
            try:
                services.request_inventory_adjustment(
                    item=form.cleaned_data['item'], warehouse=form.cleaned_data['warehouse'],
                    quantity_delta=form.cleaned_data['quantity_delta'], reason=form.cleaned_data['reason'],
                    requested_by=request.user,
                )
                messages.success(request, '已送出調整申請，待核准。')
                return redirect('inventory:adjustment_list')
            except ValidationError as e:
                _flash_validation_error(request, e)
        return render(request, self.template_name, {'form': form})


class AdjustmentApproveView(LoginRequiredMixin, View):
    def post(self, request, pk):
        adj = get_object_or_404(InventoryAdjustmentRequest, pk=pk)
        try:
            services.approve_inventory_adjustment(adj, request.user)
            messages.success(request, '已核准並套用庫存調整。')
        except ValidationError as e:
            _flash_validation_error(request, e)
        return redirect('inventory:adjustment_list')


class AdjustmentRejectView(LoginRequiredMixin, View):
    def post(self, request, pk):
        adj = get_object_or_404(InventoryAdjustmentRequest, pk=pk)
        services.reject_inventory_adjustment(adj, request.user)
        messages.success(request, '已駁回調整申請。')
        return redirect('inventory:adjustment_list')


# ---------------------------------------------------------------------------
# 循環盤點
# ---------------------------------------------------------------------------

class CycleCountListView(LoginRequiredMixin, ListView):
    model = CycleCount
    template_name = 'inventory/cycle_count_list.html'
    context_object_name = 'cycle_counts'


class CycleCountCreateView(LoginRequiredMixin, View):
    template_name = 'inventory/cycle_count_form.html'

    def get(self, request):
        return render(request, self.template_name, {'form': CycleCountCreateForm()})

    def post(self, request):
        form = CycleCountCreateForm(request.POST)
        if form.is_valid():
            item_codes = [c.strip() for c in form.cleaned_data['item_codes'].split(',') if c.strip()] or None
            cc = services.create_cycle_count(
                warehouse=form.cleaned_data['warehouse'], method=form.cleaned_data['method'],
                created_by=request.user, item_codes=item_codes,
            )
            messages.success(request, f'已建立循環盤點單 {cc.count_no}。')
            return redirect('inventory:cycle_count_detail', pk=cc.pk)
        return render(request, self.template_name, {'form': form})


class CycleCountDetailView(LoginRequiredMixin, DetailView):
    model = CycleCount
    template_name = 'inventory/cycle_count_detail.html'
    context_object_name = 'cycle_count'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['lines'] = self.object.lines.select_related('item')
        return ctx

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        action = request.POST.get('action')
        if action == 'record':
            counted = _parse_counted_qtys(request, self.object.lines.all())
            services.record_cycle_count(self.object, counted)
            messages.success(request, '已記錄實盤數量，待核准。')
        elif action == 'approve':
            try:
                services.approve_cycle_count(self.object, request.user)
                messages.success(request, '已核准並更新庫存。')
            except ValidationError as e:
                _flash_validation_error(request, e)
        return redirect('inventory:cycle_count_detail', pk=self.object.pk)


def _parse_counted_qtys(request, lines):
    counted = {}
    for line in lines:
        val = request.POST.get(f'qty_{line.pk}')
        if val not in (None, ''):
            try:
                counted[line.pk] = Decimal(val)
            except InvalidOperation:
                pass
    return counted


# ---------------------------------------------------------------------------
# 全面盤點
# ---------------------------------------------------------------------------

class PhysicalInventoryListView(LoginRequiredMixin, ListView):
    model = PhysicalInventory
    template_name = 'inventory/physical_inventory_list.html'
    context_object_name = 'physical_inventories'


class PhysicalInventoryStartView(LoginRequiredMixin, View):
    template_name = 'inventory/physical_inventory_start.html'

    def get(self, request):
        return render(request, self.template_name, {'warehouses': Warehouse.objects.filter(is_active=True)})

    def post(self, request):
        warehouse = get_object_or_404(Warehouse, pk=request.POST.get('warehouse'))
        pi = services.start_physical_inventory(warehouse, request.user)
        messages.success(request, f'已建立全面盤點單 {pi.count_no}，倉庫已凍結。')
        return redirect('inventory:physical_inventory_detail', pk=pi.pk)


class PhysicalInventoryDetailView(LoginRequiredMixin, DetailView):
    model = PhysicalInventory
    template_name = 'inventory/physical_inventory_detail.html'
    context_object_name = 'physical_inventory'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['lines'] = self.object.lines.select_related('item')
        return ctx

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        action = request.POST.get('action')
        if action == 'record':
            counted = _parse_counted_qtys(request, self.object.lines.all())
            services.import_physical_count(self.object, counted)
            messages.success(request, '已匯入盤點資料，待核准。')
        elif action == 'approve':
            try:
                services.approve_physical_inventory(self.object, request.user)
                messages.success(request, '已核准，庫存已自動調整，倉庫解除凍結。')
            except ValidationError as e:
                _flash_validation_error(request, e)
        return redirect('inventory:physical_inventory_detail', pk=self.object.pk)


# ---------------------------------------------------------------------------
# 批號 / 序號管理
# ---------------------------------------------------------------------------

class LotListView(LoginRequiredMixin, ListView):
    template_name = 'inventory/lot_list.html'
    context_object_name = 'lots'
    queryset = Lot.objects.select_related('item')


class LotCreateView(LoginRequiredMixin, CreateView):
    model = Lot
    form_class = LotForm
    template_name = 'inventory/lot_form.html'
    success_url = reverse_lazy('inventory:lot_list')


class LotUpdateView(LoginRequiredMixin, UpdateView):
    model = Lot
    form_class = LotForm
    template_name = 'inventory/lot_form.html'
    success_url = reverse_lazy('inventory:lot_list')


class SerialListView(LoginRequiredMixin, ListView):
    template_name = 'inventory/serial_list.html'
    context_object_name = 'serial_numbers'
    queryset = SerialNumberRecord.objects.select_related('item', 'warehouse')


class SerialCreateView(LoginRequiredMixin, CreateView):
    model = SerialNumberRecord
    form_class = SerialForm
    template_name = 'inventory/serial_form.html'
    success_url = reverse_lazy('inventory:serial_list')


class SerialUpdateView(LoginRequiredMixin, UpdateView):
    model = SerialNumberRecord
    form_class = SerialForm
    template_name = 'inventory/serial_form.html'
    success_url = reverse_lazy('inventory:serial_list')


# ---------------------------------------------------------------------------
# 條碼掃描
# ---------------------------------------------------------------------------

class ScanBarcodeView(LoginRequiredMixin, TemplateView):
    template_name = 'inventory/scan.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        code = self.request.GET.get('code')
        if code:
            ctx['result'] = services.scan_barcode(code)
            ctx['code'] = code
        return ctx


# ---------------------------------------------------------------------------
# 補貨建議 / 效期管理
# ---------------------------------------------------------------------------

class ReorderSuggestionView(LoginRequiredMixin, TemplateView):
    template_name = 'inventory/reorder_suggestions.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['suggestions'] = services.generate_reorder_suggestion()
        return ctx


class ExpirationView(LoginRequiredMixin, TemplateView):
    template_name = 'inventory/expiration.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['expired'] = services.get_expired_lots()
        ctx['expiring'] = services.get_expiring_lots()
        return ctx


# ---------------------------------------------------------------------------
# 交易明細 / 報表
# ---------------------------------------------------------------------------

class TransactionListView(LoginRequiredMixin, ListView):
    template_name = 'inventory/transaction_list.html'
    context_object_name = 'transactions'
    paginate_by = 50
    queryset = InventoryTransaction.objects.select_related('item', 'warehouse', 'user')


class ReportView(LoginRequiredMixin, TemplateView):
    template_name = 'inventory/report.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['report_types'] = services.REPORT_TYPES
        report_type = self.request.GET.get('report_type')
        if report_type:
            ctx['report'] = services.generate_inventory_report(report_type)
            ctx['report_type'] = report_type
        return ctx
