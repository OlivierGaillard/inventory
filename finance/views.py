from django.contrib.auth.decorators import permission_required, login_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.utils.decorators import method_decorator

from django.forms import modelformset_factory
from crispy_forms.layout import Submit
from django.shortcuts import reverse, render
from django.http import HttpResponseRedirect
from django.views.generic import CreateView, DeleteView, UpdateView
from django_filters.views import FilterView
from money import Money
from coordinates.models import Arrivage
from .models import FraisArrivage, Currency, Converter
from .forms import FraisArrivageCreateForm, FraisArrivageFormSetHelper, FraisArrivageUpdateForm
from .filters import FraisArrivageFilter


@method_decorator(login_required, name='dispatch')
#@method_decorator(permission_required('accessories.view_achat', raise_exception=True), name='dispatch')
class FraisArrivageListView(PermissionRequiredMixin, FilterView):
    #model = FraisArrivage
    template_name = "finance/list.html"
    filterset_class = FraisArrivageFilter

    permission_required = 'accessories.view_achat'
    raise_exception = True


    def get_context_data(self, **kwargs):
        context = super(FraisArrivageListView, self).get_context_data(**kwargs)
        arrivage = self.request.GET.get('arrivage_ref', '')
        devises = Currency.objects.all()
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
        if self.filterset.qs:
            context['last_arrivage_ref'] = self.filterset.qs.last().arrivage_ref
        else:
            context['arrivageID'] = arrivage
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
                                        #fields=['devise_id', 'montant', 'objet', 'date_frais'],
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
                devise = arrivage.devise
            params = "?arrivage_ref=%s&monnaie=%s" % (arrivage.pk, devise)
            url_list = reverse('finance:list') + params
            return HttpResponseRedirect(url_list)
            #return HttpResponseRedirect(reverse("finance:list"), {'last_arrivage_ref' : arrivage})
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
