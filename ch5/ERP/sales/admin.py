from django.contrib import admin

from . import models

admin.site.register(models.Customer)
admin.site.register(models.SalesOrder)
admin.site.register(models.SalesOrderItem)
admin.site.register(models.PickingList)
admin.site.register(models.PickingListLine)
admin.site.register(models.Shipment)
admin.site.register(models.ARInvoice)
