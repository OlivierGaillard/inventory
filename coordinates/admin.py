from django.contrib import admin
from .models import Pays, Localite, Adresse, Contact, ContactPhone, Fournisseur, Arrivage
    
class PaysAdmin(admin.ModelAdmin):
    list_display = ('nom', 'code')    
admin.site.register(Pays, PaysAdmin)

class LocaliteAdmin(admin.ModelAdmin):
    list_display = ('npa', 'nom')
admin.site.register(Localite, LocaliteAdmin)

class AdresseAdmin(admin.ModelAdmin):
    list_display = ('rue', 'no', 'localite', 'pays', 'visavis', 'expliq')
admin.site.register(Adresse, AdresseAdmin)

class ContactAdmin(admin.ModelAdmin):
    list_display = ('prenom', 'nom', 'phones', 'email')
admin.site.register(Contact, ContactAdmin)

class ContactPhoneAdmin(admin.ModelAdmin):
    list_display = ('contact', 'phone_number', 'phone_type')
admin.site.register(ContactPhone, ContactPhoneAdmin)

class FournisseurAdmin(admin.ModelAdmin):
    list_display = ('nom_entreprise', 'contact', 'adresse', 'email')
admin.site.register(Fournisseur, FournisseurAdmin)

class ArrivageAdmin(admin.ModelAdmin):
    list_display = ('date', 'lieu_provenance')
admin.site.register(Arrivage, ArrivageAdmin)
