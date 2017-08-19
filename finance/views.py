from django.contrib.auth.decorators import permission_required, login_required
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.utils.decorators import method_decorator
from django.http import HttpResponse
from django.forms import modelformset_factory
from crispy_forms.layout import Submit
from django.shortcuts import reverse, render
from django.http import HttpResponseRedirect
from django.views.generic import CreateView, DeleteView, UpdateView, ListView, FormView
from django.views import View
from django_filters.views import FilterView
from coordinates.models import Arrivage
from .models import FraisArrivage, Currency, Converter, Vente, ProductType
from .forms import FraisArrivageCreateForm, FraisArrivageFormSetHelper, FraisArrivageUpdateForm, CurrencyUsageForm, VenteCreateForm
from .filters import FraisArrivageFilter
from .models import Vente
from .tables import VenteTable
from products.models import Employee
from django_tables2 import RequestConfig

from crispy_forms.bootstrap import PrependedText
from crispy_forms.layout import  Hidden


@method_decorator(login_required, name='dispatch')
class FraisArrivageListView(PermissionRequiredMixin, FilterView):
    #model = FraisArrivage
    template_name = "finance/list.html"
    filterset_class = FraisArrivageFilter

    permission_required = 'accessories.view_achat'
    raise_exception = True

    def get_queryset(self):
        enterprise = Employee.get_enterprise_of_current_user(self.request.user)
        return FraisArrivage.objects.filter(arrivage_ref__enterprise=enterprise)

    def get_context_data(self, **kwargs):
        context = super(FraisArrivageListView, self).get_context_data(**kwargs)
        arrivage = self.request.GET.get('arrivage_ref', '')
        devises = Currency.objects.filter(used=True)
        monnaie = 'XOF'
        monnaie = self.request.GET.get('monnaie', '')
        if len(monnaie) == 0:
            monnaie = 'XOF'
        total =0
        devise_total = monnaie
        converter = Converter()
        for i in self.filterset.qs:
            if i.devise_id.currency_code == devise_total:
                total += i.montant
                i.montantTargetAmount = i.montant
            else:
                montant_target = i.convert(monnaie)
                i.montantTargetAmount = montant_target.amount
                total += montant_target.amount

        context['total'] = total
        context['devise_total'] = devise_total
        context['total_target'] = total
        context['devises'] = devises
        return context

@method_decorator(login_required, name='dispatch')
@method_decorator(permission_required('accessories.view_achat', raise_exception=True), name='dispatch')
class  FraisArrivageCreateView(CreateView):
    model = FraisArrivage
    template_name = "finance/create.html"
    form_class = FraisArrivageCreateForm

    def get_success_url(self):
        return reverse('finance:list')

    def get_context_data(self, **kwargs):
        context = super(FraisArrivageCreateView, self).get_context_data(**kwargs)

        formset = modelformset_factory(FraisArrivage,
                                       fields=['arrivage_ref', 'devise_id', 'montant', 'objet', 'date_frais'],
                                       form=FraisArrivageCreateForm,
                                       extra=2)
        context['formset'] = formset
        return context

@login_required
@permission_required('accessories.view_achat', raise_exception=True)
def add_frais_to_arrivage(request, pk):
    extra_rows = 1
    FraisFormset = modelformset_factory(FraisArrivage,
                                        fields=['arrivage_ref','devise_id', 'montant', 'objet', 'date_frais'],
                                        form=FraisArrivageCreateForm,
                                        can_delete=True,
                                        extra=extra_rows)

    helper = FraisArrivageFormSetHelper()
    helper.add_input(Submit("submit", "Save"))
    helper.label_class = 'col-sm-2'
    helper.field_class = 'col-sm-2'
    helper.template = 'bootstrap/table_inline_formset.html'

    if request.method == 'GET':
        arrivage = Arrivage.objects.get(pk=pk)
        dict_values = {}
        dict_values['arrivage_ref'] = arrivage

        if arrivage.devise:
            dict_values['devise_id'] = arrivage.devise
        dict_values['date_frais'] = arrivage.date

        initial_values = []
        for a in range(0, extra_rows+1):
            initial_values.append(dict_values)


        formset = FraisFormset(queryset=FraisArrivage.objects.filter(arrivage_ref=pk),
                               initial = initial_values
                               )

        return render(request, "finance/add_frais.html", {'formset': formset, 'helper': helper,
                                                          'arrivage': arrivage} )
    else:
        formset = FraisFormset(request.POST, request.FILES)
        arrivage = Arrivage.objects.get(pk=pk)
        if formset.is_valid():
            instances = formset.save()
            devise=''
            if arrivage.devise:
                devise = arrivage.devise.currency_code
            params = "?arrivage_ref=%s&monnaie=%s" % (arrivage.pk, devise)
            url_list = reverse('finance:list') + params
            return HttpResponseRedirect(url_list)
        else:
            return render(request, template_name="finance/add_frais.html",
                          context={'formset': formset, 'helper':helper})


@method_decorator(login_required, name='dispatch')
@method_decorator(permission_required('accessories.view_achat'), name='dispatch')
class FraisArrivageDeleteView(DeleteView):
    model = FraisArrivage
    template_name = "finance/delete.html"
    context_object_name = 'frais'
    fields = ['arrivage_ref', 'montant', 'objet', 'date_frais' ]

    def get_success_url(self):
        params = "?arrivage_ref=%s&monnaie=%s" % (self.object.arrivage_ref.pk, self.object.devise_id)
        url_list = reverse('finance:list') + params
        return url_list



@method_decorator(login_required, name='dispatch')
@method_decorator(permission_required('accessories.view_achat'), name='dispatch')
class FraisArrivageUpdateView(UpdateView):
    model = FraisArrivage
    template_name = "finance/update.html"
    context_object_name = 'frais'
    #fields = ['montant', 'objet', 'date_frais']
    form_class = FraisArrivageUpdateForm


    def get_success_url(self):
        params = "?arrivage_ref=%s&monnaie=%s" % (self.object.arrivage_ref.pk, self.object.devise_id)
        url_list = reverse('finance:list') + params
        return url_list



@method_decorator(login_required, name='dispatch')
@method_decorator(permission_required('accessories.view_achat'), name='dispatch')
class CurrencyUsageView(UpdateView):
    template_name = 'finance/update.html'
    context_object_name = 'currency'
    model = Currency
    form_class = CurrencyUsageForm

    def get_success_url(self):
        return reverse('finance:currencies')


class CurrencyListView(ListView):
    model = Currency
    template_name = 'finance/currencies.html'
    context_object_name = 'currencies'


@login_required
@user_passes_test(Employee.is_current_user_employee)
def ventes(request):
    """If the enterprise of the user has no data it returns an empty list."""
    enterprise_of_current_user = Employee.get_enterprise_of_current_user(request.user)

    q = Vente.objects.filter(product_owner=enterprise_of_current_user)
    table = None
    if q.exists():
        table = VenteTable(q)
    else:
        table = VenteTable([])
    RequestConfig(request).configure(table)
    return render(request, 'finance/ventes.html', {'table' : table})



@login_required
def make_selling(request, product_id, product_type):
    """
    This view allows the user to enter quantity and client for a selling.

    Keyword arguments:

    product_id   -- the primary key of one article of type product_type.

    product_type -- one instance of the model finance.ProductType. The three used
    in this application are:

    1. Clothes

    2. Shoe

    3. Accessory

    The field 'client_id' is a foreign key to the model coordinates.Contact. It
    has a drop-down list to choose from.
    """

    def get_concrete_article_and_product_type(product_type, product_id):
        product_type = ProductType.objects.get(model_class=product_type)
        product_cls = product_type.get_concrete_class()
        article = product_cls.objects.get(pk=product_id)
        remaining = article.get_quantity()
        return (article, product_type, remaining)

    if request.method == 'GET':
        article, product_type, remaining = get_concrete_article_and_product_type(product_type, product_id)
        data = {'product_id' : product_id,
                'product_type' : product_type.pk,
                'quantity' : '1'}

        form = VenteCreateForm(data)
        form.helper.layout.append(PrependedText('quantity', 'Max: ' + str(remaining)))
        return render(request, "finance/create_vente.html", {'form': form, 'article' : article})

    else:
        form = VenteCreateForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('finance:ventes'))
        else:
            article, product_type, remaining = get_concrete_article_and_product_type(product_type, product_id)
            form.helper.layout.append(PrependedText('quantity', 'Max: ' + str(remaining)))
            return render(request, "finance/create_vente.html", {'form': form, 'article': article})


class SellingView(FormView):

    form_class = VenteCreateForm
    template_name = "finance/create_vente.html"

    def get_concrete_article_and_product_type(self, product_type, product_id):
        product_type = ProductType.objects.get(model_class=product_type)
        product_cls = product_type.get_concrete_class()
        article = product_cls.objects.get(pk=product_id)
        remaining = article.get_quantity()
        return (article, product_type, remaining)


    def get(self, request, *args, **kwargs):
        product_id   = kwargs['product_id']
        product_type = kwargs['product_type']
        article, product_type, remaining = self.get_concrete_article_and_product_type(product_type, product_id)

        data = {'product_id': product_id,
                'product_type': product_type.pk}

        print(data)
        form = self.form_class(initial=data)
        # form.helper.layout.append(Hidden('product_type', product_type.pk))
        # form.helper.layout.append(Hidden('product_id',   str(product_id)))

        form.helper.layout.append(PrependedText('quantity', 'Max: ' + str(remaining)))
        return render(request, self.template_name, {'form': form, 'article': article, 'remaining' : remaining})

    def post(self, request, *args, **kwargs):
        form = VenteCreateForm(request.POST)
        print(form.is_bound)
        print(form.cleaned_data())
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('finance:ventes'))
        else:
            product_id   = kwargs['product_id']
            product_type = kwargs['product_type']
            article, product_type, remaining = self.get_concrete_article_and_product_type(product_type, product_id)
            return render(request, self.template_name, {'form': form, 'article': article, 'remaining': remaining})


