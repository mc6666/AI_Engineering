from django.urls import path

from . import views

app_name = 'sales'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),

    path('customers/', views.CustomerListView.as_view(), name='customer_list'),
    path('customers/add/', views.CustomerCreateView.as_view(), name='customer_add'),

    path('orders/', views.SalesOrderListView.as_view(), name='order_list'),
    path('orders/add/', views.SalesOrderCreateView.as_view(), name='order_add'),
    path('orders/<int:pk>/', views.SalesOrderDetailView.as_view(), name='order_detail'),
    path('orders/<int:pk>/submit/', views.SubmitOrderView.as_view(), name='order_submit'),
    path('orders/<int:pk>/approve/', views.ApproveOrderView.as_view(), name='order_approve'),
    path('orders/<int:pk>/cancel/', views.CancelOrderView.as_view(), name='order_cancel'),
    path('orders/<int:pk>/close/', views.CloseOrderView.as_view(), name='order_close'),
    path('orders/<int:pk>/duplicate/', views.DuplicateOrderView.as_view(), name='order_duplicate'),
    path('orders/<int:pk>/picking-list/', views.GeneratePickingListView.as_view(), name='order_picking_list'),
    path('orders/<int:pk>/ship/', views.CreateShipmentView.as_view(), name='order_ship'),
    path('orders/<int:pk>/invoice/', views.CreateInvoiceView.as_view(), name='order_invoice'),

    path('invoices/<int:pk>/payment/', views.RecordPaymentView.as_view(), name='invoice_payment'),

    path('export/csv/', views.ExportCSVView.as_view(), name='export_csv'),
    path('export/excel/', views.ExportExcelView.as_view(), name='export_excel'),
    path('export/pdf/', views.ExportPDFView.as_view(), name='export_pdf'),
    path('import/', views.ImportCSVView.as_view(), name='import_csv'),
]
