from django.conf.urls import url
from . import views


app_name = 'finance'

urlpatterns = [
    url(r'^create/$', views.FraisArrivageCreateView.as_view(), name='create'),
    url(r'^add_frais/(?P<pk>[0-9]*)$', views.add_frais_to_arrivage, name='add_frais'),
    url(r'^list/([0-9])*$', views.FraisArrivageListView.as_view(), name='list'),
    url(r'^delete/(?P<pk>[0-9]+)$', views.FraisArrivageDeleteView.as_view(), name='delete'),
    url(r'^update/(?P<pk>[0-9]+)$', views.FraisArrivageUpdateView.as_view(), name='update'),
    url(r'^currencies/$', views.CurrencyListView.as_view(), name='currencies'),
    url(r'^update_currency/(?P<pk>[0-9]+)$', views.CurrencyUsageView.as_view(), name='update_currency'),
    url(r'^ventes/$', views.ventes, name='ventes'),
    # To sell product-ID
    url(r'^create_vente/(?P<product_id>[0-9]+)/(?P<product_type>.+)$', views.make_selling, name='create_vente'),
    #url(r'^create_vente/(?P<product_id>[0-9]+)/(?P<product_type>.+)$', views.SellingView.as_view(), name='create_vente'),
    ]
