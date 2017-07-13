from django.conf.urls import url
from . import views


app_name = 'shoes'

# TODO: add UpdateView

urlpatterns = [
    url(r'^shoe_create/$', views.ShoeCreationView.as_view(), name='shoe_create'),
    url(r'^categorie_create/$', views.CategoryCreationView.as_view(), name='category_create'),
    url(r'^shoes_list/$', views.ShoeListView.as_view(), name='shoe-list'),
    url(r'^categories_list/$', views.CategoryListView.as_view(), name='category-list'),
    url(r'^inventaire/$', views.InventoryListView.as_view(), name='inventory'),
    url(r'^inventaire_create/$', views.InventoryCreationView.as_view(), name='inventory_create'),
    ]