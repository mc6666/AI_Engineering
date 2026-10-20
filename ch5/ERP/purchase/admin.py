from django.contrib import admin

from . import models

admin.site.register(models.Supplier)
admin.site.register(models.PurchaseRequisition)
admin.site.register(models.PurchaseRequisitionItem)
admin.site.register(models.RFQ)
admin.site.register(models.RFQSupplier)
admin.site.register(models.Quotation)
admin.site.register(models.PurchaseOrder)
admin.site.register(models.PurchaseOrderItem)
admin.site.register(models.GoodsReceipt)
admin.site.register(models.GoodsReceiptItem)
admin.site.register(models.SupplierReturn)
admin.site.register(models.SupplierInvoice)
admin.site.register(models.PaymentSchedule)
