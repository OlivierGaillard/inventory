from django.contrib import admin
from django_mptt_admin.admin import DjangoMpttAdmin
from .models import Accessory, AccessoryEntry, InventoryAccessory, AccessoryCategory

# Register your models here.

class AcessoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'marque_ref']
admin.site.register(Accessory, AcessoryAdmin)

class AccessoryEntryAdmin(admin.ModelAdmin):
    list_display = ['article', 'date', 'creation_date', 'quantity']

admin.site.register(AccessoryEntry, AccessoryEntryAdmin)

class InventoryAccessoryAdmin(admin.ModelAdmin):
    list_display = ['date', 'article', 'quantity']

admin.site.register(InventoryAccessory, InventoryAccessoryAdmin)

admin.site.register(AccessoryCategory)

