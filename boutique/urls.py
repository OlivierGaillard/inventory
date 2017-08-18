"""boutique URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls import url
from django.contrib import admin
from django.conf.urls import include
from django.conf.urls.static import static
from django.views.generic import TemplateView
from .views import IndexView

urlpatterns = [
    # url(r'^inventex/', include('inventex.urls', namespace="inventex")),
    url(r'^accessories/', include('accessories.urls', namespace="accessories")),
    url(r'^shoes/', include('shoes.urls', namespace="shoes")),
    url(r'^clothes/', include('clothes.urls', namespace="clothes")),
    #url(r'^$', TemplateView.as_view(template_name='index.html'), name='home'),
    url(r'^$', IndexView.as_view(), name='home'),
    url(r'^coordinates/', include('coordinates.urls', namespace="coordinates")),
    url(r'^accounts/', include('accounts.urls', namespace="accounts")),
    url(r'^finance/', include('finance.urls', namespace="finance")),
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', admin.site.urls),] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
