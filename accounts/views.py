from django.contrib.auth.views import LoginView
from django.contrib.auth.forms import UserCreationForm
from django.views.generic import CreateView, TemplateView


# Create your views here.

class MyLoginView(LoginView):
    template_name = 'login.html'

class ThanksView(TemplateView):
    template_name = 'thanks.html'


class UserRegistrationView(CreateView):
    """
    TODO: add the enterprise.
    """
    form_class = UserCreationForm
    template_name = 'accounts/user_registration.html'
    
    def get_success_url(self):
        #return reverse('index')
        return ("/")


