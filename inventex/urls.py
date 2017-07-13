from django.conf.urls import url
from django.views.generic import TemplateView
from . import views


app_name = 'inventex'

urlpatterns = [
    url(r'^$', TemplateView.as_view(template_name='index.html'), name='home'),
    url(r'article-create/', views.ArticleCreationView.as_view(), name='article-create'),
    url(r'articles/(?P<pk>[0-9]+)$', views.ArticleDetailView.as_view(), name='article-detail'),
    url(r'^article-update/(?P<pk>[0-9]+)$', views.ArticleUpdateView.as_view(), name='article-update'),
    url(r'^article-delete/(?P<pk>[0-9]+)$', views.ArticleDeleteView.as_view(), name='article-delete'),
    url(r'articles/', views.ArticlesList.as_view(), name ='articles-list'),
    url(r'entrees/', views.EntreesList.as_view(), name ='entrees-list'),
    ]
#url(r'test-form/$', views.make_article),