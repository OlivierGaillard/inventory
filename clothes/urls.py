from django.conf.urls import url
from . import views


app_name = 'clothes'


urlpatterns = [
    url(r'^clothes_create/$', views.ClothesCreationView.as_view(), name='clothes_create'),
    url(r'^list/$', views.ClothesListView.as_view(), name='list'),
    url(r'detail/(?P<pk>[0-9]+)$', views.ClothesDetailView.as_view(), name='detail'),
    url(r'^delete/(?P<pk>[0-9]+)$', views.ClothesDeleteView.as_view(), name='delete'),
    url(r'^update/(?P<pk>[0-9]+)$', views.ClothesUpdateView.as_view(), name='update'),

    url(r'^upload_pic/(?P<pk>[0-9]+)$', views.upload_pic, name='upload_pic'),
    url(r'^photo_delete/(?P<pk>[0-9]+)$', views.PhotoDeleteView.as_view(), name='photo_delete'),

    url(r'^categories_list/$', views.CategoryListView.as_view(), name='category-list'),
    url(r'^categorie_create/$', views.CategoryCreationView.as_view(), name='category_create'),
    url(r'^category-update/(?P<pk>[0-9]+)$', views.CategoryUpdateView.as_view(), name='category-update'),


    url(r'^inventaire/$', views.InventoryListView.as_view(), name='inventory'),
    url(r'^inventaire_create/$', views.InventoryCreationView.as_view(), name='inventory_create'),
    ]