from django.conf.urls import url
from django.contrib.auth import views
from django.contrib.auth.views import logout
from .views import MyLoginView, ThanksView

app_name = 'accounts'
urlpatterns = [
    url(r'^login/$', MyLoginView.as_view(), name='login'),
    url(r'^thanks/$', ThanksView.as_view(), name='thanks'),
    url(r'^logout/$', logout, {'next_page': '/accounts/thanks/',  }, name='logout'),
    ]
