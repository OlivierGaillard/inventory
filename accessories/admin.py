from django.contrib import admin
from django_mptt_admin.admin import DjangoMpttAdmin
from mptt.admin import DraggableMPTTAdmin
from .models import Accessory, AccessoryEntry, InventoryAccessory, AccessoryCategory, Photo

# Register your models here.

admin.site.register(
    AccessoryCategory,
    DraggableMPTTAdmin,
    list_display=(
        'tree_actions',
        'indented_title',
        # ...more fields if you feel like it...
    ),
    list_display_links=(
        'indented_title',
    ),
)

class AccessoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'marque_ref', 'product_owner']
admin.site.register(Accessory, AccessoryAdmin)

class AccessoryEntryAdmin(admin.ModelAdmin):
    list_display = ['article', 'date', 'creation_date', 'quantity']

admin.site.register(AccessoryEntry, AccessoryEntryAdmin)

class InventoryAccessoryAdmin(admin.ModelAdmin):
    list_display = ['date', 'article', 'quantity']

admin.site.register(InventoryAccessory, InventoryAccessoryAdmin)


class PhotoAdmin(admin.ModelAdmin):
    list_display = ['legende', 'photo']

admin.site.register(Photo, PhotoAdmin)

