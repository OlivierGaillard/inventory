from django.conf.urls import url
from . import views


app_name = 'labels'

urlpatterns = [
    url(r'^labelsforclothes/$', views.clothes_labels, name='clothes_labels'),
]
