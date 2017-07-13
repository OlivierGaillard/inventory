from django.contrib import admin

# Register your models here
from .models import Article, Photo, Entree, Marque

admin.site.register(Marque)

class ArticleAdmin(admin.ModelAdmin):
    list_display = ('modele', 'type_client', 'type_de_produit', )
          
    
admin.site.register(Article, ArticleAdmin)


# class PhotoAdmin(admin.ModelAdmin):
#     list_display = ('photo', 'legende')
admin.site.register(Photo)


class EntreeAdmin(admin.ModelAdmin):
    list_display = ('date', 'article', 'quantity')
admin.site.register(Entree, EntreeAdmin)