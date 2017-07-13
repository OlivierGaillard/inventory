from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.contrib.auth.views import login
from django.contrib.auth.forms import UserCreationForm
from django.core.urlresolvers import reverse
from django.views.generic import CreateView


# Create your views here.
class UserRegistrationView(CreateView):
    form_class = UserCreationForm
    template_name = 'accounts/user_registration.html'
    
    def get_success_url(self):
        #return reverse('index')
        return ("/")


