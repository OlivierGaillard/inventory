from django.contrib import admin
from mptt.admin import DraggableMPTTAdmin
from .models import Clothes, ClothesEntry, InventoryClothes, ClothesCategory

# Register your models here.
#admin.site.register(ClothesCategory, MPTTModelAdmin)

admin.site.register(
    ClothesCategory,
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