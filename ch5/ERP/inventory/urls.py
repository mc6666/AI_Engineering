from django.urls import path

from . import views

app_name = 'inventory'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),

    path('items/', views.ItemListView.as_view(), name='item_list'),
    path('items/add/', views.ItemCreateView.as_view(), name='item_add'),
    path('items/<int:pk>/', views.ItemDetailView.as_view(), name='item_detail'),
    path('items/<int:pk>/edit/', views.ItemUpdateView.as_view(), name='item_edit'),
    path('items/<int:pk>/delete/', views.ItemDeleteView.as_view(), name='item_delete'),
    path('items/<int:pk>/barcode/generate/', views.GenerateBarcodeView.as_view(), name='item_generate_barcode'),

    path('categories/', views.ItemCategoryListView.as_view(), name='category_list'),
    path('categories/add/', views.ItemCategoryCreateView.as_view(), name='category_add'),
    path('categories/<int:pk>/delete/', views.ItemCategoryDeleteView.as_view(), name='category_delete'),

    path('warehouses/', views.WarehouseListView.as_view(), name='warehouse_list'),
    path('warehouses/add/', views.WarehouseCreateView.as_view(), name='warehouse_add'),
    path('warehouses/<int:pk>/', views.WarehouseDetailView.as_view(), name='warehouse_detail'),
    path('warehouses/<int:pk>/edit/', views.WarehouseUpdateView.as_view(), name='warehouse_edit'),
    path('warehouses/<int:pk>/delete/', views.WarehouseDeleteView.as_view(), name='warehouse_delete'),
    path('warehouses/<int:warehouse_pk>/bins/add/', views.BinCreateView.as_view(), name='bin_add'),
    path('bins/<int:pk>/delete/', views.BinDeleteView.as_view(), name='bin_delete'),

    path('stock/search/', views.StockSearchView.as_view(), name='stock_search'),
    path('stock/receive/', views.ReceiveInventoryView.as_view(), name='receive'),
    path('stock/issue/', views.IssueInventoryView.as_view(), name='issue'),
    path('stock/transfer/', views.TransferInventoryView.as_view(), name='transfer'),
    path('stock/reserve/', views.ReserveInventoryView.as_view(), name='reserve'),
    path('stock/release/', views.ReleaseReservationView.as_view(), name='release'),

    path('adjustments/', views.AdjustmentRequestListView.as_view(), name='adjustment_list'),
    path('adjustments/add/', views.AdjustmentRequestCreateView.as_view(), name='adjustment_add'),
    path('adjustments/<int:pk>/approve/', views.AdjustmentApproveView.as_view(), name='adjustment_approve'),
    path('adjustments/<int:pk>/reject/', views.AdjustmentRejectView.as_view(), name='adjustment_reject'),

    path('cycle-counts/', views.CycleCountListView.as_view(), name='cycle_count_list'),
    path('cycle-counts/add/', views.CycleCountCreateView.as_view(), name='cycle_count_add'),
    path('cycle-counts/<int:pk>/', views.CycleCountDetailView.as_view(), name='cycle_count_detail'),

    path('physical-inventories/', views.PhysicalInventoryListView.as_view(), name='physical_inventory_list'),
    path('physical-inventories/start/', views.PhysicalInventoryStartView.as_view(), name='physical_inventory_start'),
    path('physical-inventories/<int:pk>/', views.PhysicalInventoryDetailView.as_view(), name='physical_inventory_detail'),

    path('lots/', views.LotListView.as_view(), name='lot_list'),
    path('lots/add/', views.LotCreateView.as_view(), name='lot_add'),
    path('lots/<int:pk>/edit/', views.LotUpdateView.as_view(), name='lot_edit'),

    path('serials/', views.SerialListView.as_view(), name='serial_list'),
    path('serials/add/', views.SerialCreateView.as_view(), name='serial_add'),
    path('serials/<int:pk>/edit/', views.SerialUpdateView.as_view(), name='serial_edit'),

    path('scan/', views.ScanBarcodeView.as_view(), name='scan'),
    path('reorder-suggestions/', views.ReorderSuggestionView.as_view(), name='reorder_suggestions'),
    path('expiration/', views.ExpirationView.as_view(), name='expiration'),

    path('transactions/', views.TransactionListView.as_view(), name='transaction_list'),
    path('reports/', views.ReportView.as_view(), name='report'),
]
