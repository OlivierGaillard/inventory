from django.conf.urls import url
from . import views


app_name = 'accessories'

urlpatterns = [
    url(r'^create/$', views.AccessoryCreationView.as_view(), name='create'),
    url(r'^update/(?P<pk>[0-9]+)$', views.AccessoryUpdateView.as_view(), name='update'),
    url(r'^delete/(?P<pk>[0-9]+)$', views.AccessoryDeleteView.as_view(), name='delete'),
    url(r'^list/$', views.AccessoryListView.as_view(), name='list'),
    url(r'detail/(?P<pk>[0-9]+)$', views.AccessoryDetailView.as_view(), name='detail'),

    url(r'^category-list/$', views.CategoryListView.as_view(), name='category-list'),
    url(r'^category-create/$', views.CategoryCreationView.as_view(), name='category-create'),

    url(r'^inventory-list/$', views.InventoryListView.as_view(), name='inventory-list'),
    url(r'^inventory-create/$', views.InventoryCreationView.as_view(), name='inventory-create'),
    url(r'^upload_pic/(?P<pk>[0-9]+)$', views.upload_pic, name='upload_pic'),
    url(r'^photo_delete/(?P<pk>[0-9]+)$', views.PhotoDeleteView.as_view(), name='photo_delete'),
    ]