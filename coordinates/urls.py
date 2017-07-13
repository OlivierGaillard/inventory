from django.conf.urls import  url
from coordinates.views import ArrivageCreationView, ArrivageUpdateView, ArrivageListView, ArrivageDetailView, ArrivageDeleteView, FournisseurCreationView, FournisseurListView
from coordinates.views import ContactListView, ContactCreationView
from coordinates import views

app_name = 'coordinates'
urlpatterns = [
    url(r'^arrivage-create/$', ArrivageCreationView.as_view(), name='arrivage-create'),
    url(r'^arrivage/(?P<pk>[0-9]+)$', ArrivageDetailView.as_view(), name='arrivage-detail'),
    url(r'^arrivage-update/(?P<pk>[0-9]+)$', ArrivageUpdateView.as_view(), name='arrivage-update'),
    url(r'^arrivage-delete/(?P<pk>[0-9]+)$', ArrivageDeleteView.as_view(), name='arrivage-delete'),
    url(r'^arrivages/$', ArrivageListView.as_view(), name='arrivages'),
    url(r'^fournisseur-create/$', FournisseurCreationView.as_view(), name='fournisseur-create'),
    url(r'^fournisseurs/$', FournisseurListView.as_view(), name='fournisseurs-list'),
    url(r'^contact-create/$', ContactCreationView.as_view(), name='contact-create'),
    url(r'^contacts/$', ContactListView.as_view(), name='contacts-list'),
    url(r'^location-create/$', views.LocationCreationView.as_view() , name='location-create'),
    url(r'^locations/$', views.LocationListView.as_view() , name='locations'),
    url(r'^location-update/(?P<pk>[0-9]+)$', views.LocationUpdateView.as_view() , name='location-update'),
    url(r'^location-delete/(?P<pk>[0-9]+)$', views.LocationDeleteView.as_view() , name='location-delete'),
    ]
