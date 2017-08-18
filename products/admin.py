from django.contrib import admin
from .models import Marque, Enterprise, Employee

# Register your models here.
admin.site.register(Marque)
admin.site.register(Enterprise)

class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['user', 'enterprise']

admin.site.register(Employee, EmployeeAdmin)
