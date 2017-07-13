from django.conf.urls import url
from . import views


app_name = 'clothes'

# TODO: add UpdateView

urlpatterns = [
    url(r'^clothes_create/$', views.ClothesCreationView.as_view(), name='clothes_create'),
    url(r'^categorie_create/$', views.CategoryCreationView.as_view(), name='category_create'),
    url(r'^clothes_list/$', views.ClothesListView.as_view(), name='clothes-list'),
    url(r'^categories_list/$', views.CategoryListView.as_view(), name='category-list'),
    url(r'^inventaire/$', views.InventoryListView.as_view(), name='inventory'),
    url(r'^inventaire_create/$', views.InventoryCreationView.as_view(), name='inventory_create'),
    ]