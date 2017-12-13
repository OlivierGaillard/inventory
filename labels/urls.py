from django.conf.urls import url
from . import views


app_name = 'labels'

urlpatterns = [
    url(r'^labels_tex/(?P<article_type>\w+)$', views.labels_tex, name='labels'),
]
