from django.contrib import admin
from .models import ShoeCategory, Shoe

# Register your models here.
admin.site.register(Shoe)
admin.site.register(ShoeCategory)