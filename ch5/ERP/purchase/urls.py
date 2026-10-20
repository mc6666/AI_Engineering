from django.urls import path

from . import views

app_name = 'purchase'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),

    path('suppliers/', views.SupplierListView.as_view(), name='supplier_list'),
    path('suppliers/add/', views.SupplierCreateView.as_view(), name='supplier_add'),
    path('suppliers/<int:pk>/edit/', views.SupplierUpdateView.as_view(), name='supplier_edit'),
    path('suppliers/<int:pk>/delete/', views.SupplierDeleteView.as_view(), name='supplier_delete'),
    path('suppliers/scorecard/', views.SupplierScorecardView.as_view(), name='supplier_scorecard'),

    path('requisitions/', views.PurchaseRequisitionListView.as_view(), name='requisition_list'),
    path('requisitions/add/', views.PurchaseRequisitionCreateView.as_view(), name='requisition_add'),
    path('requisitions/<int:pk>/', views.PurchaseRequisitionDetailView.as_view(), name='requisition_detail'),
    path('requisitions/<int:pk>/lines/add/', views.RequisitionAddLineView.as_view(), name='requisition_add_line'),
    path('requisitions/<int:pk>/approve/', views.RequisitionApproveView.as_view(), name='requisition_approve'),
    path('requisitions/<int:pk>/reject/', views.RequisitionRejectView.as_view(), name='requisition_reject'),

    path('rfqs/', views.RFQListView.as_view(), name='rfq_list'),
    path('rfqs/add/', views.RFQCreateView.as_view(), name='rfq_add'),
    path('rfqs/<int:pk>/', views.RFQDetailView.as_view(), name='rfq_detail'),
    path('rfqs/<int:pk>/send/', views.RFQSendView.as_view(), name='rfq_send'),
    path('rfqs/<int:pk>/quotations/add/', views.QuotationCreateView.as_view(), name='quotation_add'),

    path('orders/', views.PurchaseOrderListView.as_view(), name='order_list'),
    path('orders/add/', views.PurchaseOrderCreateView.as_view(), name='order_add'),
    path('orders/<int:pk>/', views.PurchaseOrderDetailView.as_view(), name='order_detail'),
    path('orders/<int:pk>/lines/add/', views.POAddLineView.as_view(), name='order_add_line'),
    path('orders/<int:pk>/submit/', views.POSubmitView.as_view(), name='order_submit'),
    path('orders/<int:pk>/approve/', views.POApproveView.as_view(), name='order_approve'),
    path('orders/<int:pk>/send/', views.POSendView.as_view(), name='order_send'),
    path('orders/<int:pk>/confirm-supplier/', views.POConfirmSupplierView.as_view(), name='order_confirm_supplier'),
    path('orders/<int:pk>/cancel/', views.POCancelView.as_view(), name='order_cancel'),
    path('orders/<int:pk>/close/', views.POCloseView.as_view(), name='order_close'),
    path('orders/<int:pk>/receive/', views.GoodsReceiptCreateView.as_view(), name='order_receive'),
    path('orders/<int:pk>/invoice/add/', views.SupplierInvoiceCreateView.as_view(), name='order_invoice_add'),

    path('goods-receipts/<int:pk>/', views.GoodsReceiptDetailView.as_view(), name='goods_receipt_detail'),
    path('goods-receipts/lines/<int:pk>/inspect/', views.QualityInspectionView.as_view(), name='goods_receipt_line_inspect'),
    path('goods-receipts/lines/<int:pk>/return/', views.SupplierReturnCreateView.as_view(), name='goods_receipt_line_return'),

    path('invoices/<int:pk>/', views.SupplierInvoiceDetailView.as_view(), name='invoice_detail'),
    path('invoices/<int:pk>/three-way-match/', views.ThreeWayMatchView.as_view(), name='invoice_three_way_match'),
    path('invoices/<int:pk>/schedule-payment/', views.SchedulePaymentView.as_view(), name='invoice_schedule_payment'),
    path('payments/<int:pk>/mark-paid/', views.MarkPaymentPaidView.as_view(), name='payment_mark_paid'),

    path('reorder-suggestions/', views.ReorderSuggestionView.as_view(), name='reorder_suggestions'),
]
