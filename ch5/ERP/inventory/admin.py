from django.contrib import admin

from . import models

admin.site.register(models.ItemCategory)
admin.site.register(models.Item)
admin.site.register(models.Warehouse)
admin.site.register(models.Bin)
admin.site.register(models.Lot)
admin.site.register(models.SerialNumberRecord)
admin.site.register(models.StockLevel)
admin.site.register(models.InventoryTransaction)
admin.site.register(models.InventoryAdjustmentRequest)
admin.site.register(models.CycleCount)
admin.site.register(models.CycleCountLine)
admin.site.register(models.PhysicalInventory)
admin.site.register(models.PhysicalInventoryLine)
