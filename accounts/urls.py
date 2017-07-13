from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static
from django.contrib.auth.views import login
from django.contrib.auth.views import logout
from django.views.generic import TemplateView
from accounts.views import UserRegistrationView

app_name = 'accounts'
urlpatterns = [
    url(r'^login/$', login, {'template_name': 'login.html'}, name='login'),
    url(r'^logout/$', logout, {'next_page': '/'}, name='logout'),
    ]
