from django.contrib import admin

# Register your models here.
from .models import Currency, FraisType, Achat, Tarif, FraisArrivage

class CurrencyAdmin(admin.ModelAdmin):
    list_display = ('currency_code', 'rate_usd', 'last_update')

admin.site.register(Currency, CurrencyAdmin)

admin.site.register(FraisType)

# class FraisArrivageAdmin(admin.ModelAdmin):
#     list_display = ('objet', 'montant', 'devise_id', 'frais_type', 'date_frais')
#
# admin.site.register(Frais, FraisAdmin)

class AchatAdmin(admin.ModelAdmin):
    list_display = ('objet', 'quantite', 'date_achat', 'montant', 'devise_id')
    
admin.site.register(Achat, AchatAdmin)

class TarifAdmin(admin.ModelAdmin):
    list_display = ('achat', 'prix_vente_min')
    
admin.site.register(Tarif, TarifAdmin)

admin.site.register(FraisArrivage)