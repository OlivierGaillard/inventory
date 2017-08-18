from django.db.models import ObjectDoesNotExist
from django.views.generic import TemplateView
from django.contrib.auth.models import User
from products.models import Enterprise, Employee

class IndexView(TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        user = self.request.user
        if user.is_authenticated():
            try:
                context['employee'] = Employee.objects.get(user=user)
            except ObjectDoesNotExist:
                context['employee'] = None
        return context