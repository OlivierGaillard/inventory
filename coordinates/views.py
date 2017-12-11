from django.views.generic import CreateView, UpdateView, DetailView, DeleteView, ListView
from django.urls import reverse
from django.contrib.auth.decorators import permission_required, login_required
from django.conf import settings
from django.utils.decorators import method_decorator
from django.db.models import Sum
from products.models import Enterprise, Employee
from finance.models import Currency, FraisArrivage, Vente
from coordinates.models import Pays
from .models import Arrivage, Fournisseur, Contact, Localite
from .forms import ArrivageCreateForm, ArrivageUpdateForm, LocaliteCreateForm, LocaliteUpdateForm



class LocationListView(ListView):
    model = Localite
    template_name = 'coordinates/locations.html'
    context_object_name = 'locations'

@method_decorator(login_required, name='dispatch')
@method_decorator(permission_required('accessories.view_achat', raise_exception=True), name='dispatch')
class LocationCreationView(CreateView):
    model = Localite
    form_class = LocaliteCreateForm
    template_name = 'coordinates/location-create.html'

    def get_success_url(self):
        return reverse('coordinates:locations')

@method_decorator(login_required, name='dispatch')
@method_decorator(permission_required('accessories.view_achat', raise_exception=True), name='dispatch')
class LocationUpdateView(UpdateView):
    model = Localite
    form_class = LocaliteUpdateForm
    template_name = 'coordinates/location-update.html'
    context_object_name = 'location'

    def get_success_url(self):
        return reverse('coordinates:locations')

@method_decorator(login_required, name='dispatch')
@method_decorator(permission_required('accessories.view_achat', raise_exception=True), name='dispatch')
class LocationDeleteView(DeleteView):
    model = Localite
    template_name = 'coordinates/location-delete.html'
    context_object_name = 'location'

    def get_success_url(self):
        return reverse('coordinates:locations')




@method_decorator(login_required, name='dispatch')
@method_decorator(permission_required('accessories.view_achat', raise_exception=True), name='dispatch')
class ArrivageCreationView(CreateView):
    """
    One arrival is bounded to the enterprise of the current logged employee.
    This information is displayed as a disabled select drop-down list.

    Only users granted may create arrivals. If one user is granted but still not an
    employee he is redirected to the part of the login page explaining this case.
    **TODO: add the UserPassesTestMixin.**
    """
    model = Arrivage
    template_name = 'coordinates/arrivage-create.html'
    form_class = ArrivageCreateForm


    def get_initial(self):
        initial = super(ArrivageCreationView, self).get_initial()
        initial['devise'] = Currency.objects.first()
        enterprise = Employee.get_enterprise_of_current_user(self.request.user)
        initial['enterprise'] = enterprise.pk
        return initial

    def get_success_url(self):
        return reverse('coordinates:arrivages')


@method_decorator(login_required, name='dispatch')
@method_decorator(permission_required('accessories.view_achat', raise_exception=True), name='dispatch')
class ArrivageDetailView(DetailView):
    model = Arrivage
    template_name = 'coordinates/arrivage.html'
    fields = ('date', 'designation', 'lieu_provenance', 'pays')



@method_decorator(login_required, name='dispatch')
@method_decorator(permission_required('accessories.view_achat', raise_exception=True), name='dispatch')
class ArrivageUpdateView(UpdateView):
    model = Arrivage
    form_class = ArrivageUpdateForm
    template_name = 'coordinates/arrivage-update.html'

    def get_initial(self):
        initial = super(ArrivageUpdateView, self).get_initial()
        if self.object.devise is None:
            initial['devise'] = Currency.objects.filter(used=True).first()
        else:
            initial['devise'] = self.object.devise

        if self.object.pays is None:
            initial['pays'] = Pays.objects.first()
        return initial

    def form_valid(self, form):
        devise = form['devise'].value()
        currency = Currency.objects.get(pk=devise)
        currency.used = True
        currency.save()
        return super(ArrivageUpdateView, self).form_valid(form)


    def get_success_url(self):
        return reverse('coordinates:arrivage-detail', kwargs={'pk': self.object.pk})

@method_decorator(login_required, name='dispatch')
class ArrivageListView(ListView):
    model = Arrivage
    template_name = 'coordinates/arrivages.html'
    context_object_name = 'liste'

    def get_queryset(self):
        enterprise = Employee.get_enterprise_of_current_user(self.request.user)
        return Arrivage.objects.filter(enterprise=enterprise)


    def get_context_data(self, **kwargs):
        """To calculate the total of frais and achats."""
        context = super(ArrivageListView, self).get_context_data(**kwargs)
        arrivages = self.get_queryset()
        total_frais = 0
        total_frais_all_inventories = 0
        total_achats = 0
        total_achats_all_inventories = 0
        try:
            target_currency = Currency.objects.filter(default=True)[0]
        except:
            raise Exception("Please set a default currency using admin.")
        context['target_currency'] = target_currency

        for a in arrivages:
            total_achats += a.get_total_achats()
            total_achats_all_inventories += total_achats
            total_frais  += a.get_total_frais()
            total_frais_all_inventories += total_frais
        context['total_achats'] = total_achats
        context['total_frais']  = total_frais
        context['target_currency'] = target_currency
        context['total_frais_all_inventories']  = total_frais_all_inventories
        context['total_achats_all_inventories'] = total_achats_all_inventories
        context['total_cout_revient'] = total_achats_all_inventories + total_frais_all_inventories
        enterprise_of_current_user = Employee.get_enterprise_of_current_user(self.request.user)
        q = Vente.objects.filter(product_owner=enterprise_of_current_user)

        if q.exists():
            e_sum = q.aggregate(Sum('montant'))
            e_sum = e_sum['montant__sum']
            context['total_ventes'] = e_sum
            solde = e_sum - (total_frais_all_inventories + total_achats_all_inventories)
            context['solde'] = solde
        return context


@method_decorator(login_required, name='dispatch')
@method_decorator(permission_required('accessories.view_achat', raise_exception=True), name='dispatch')
class ArrivageDeleteView(DeleteView):
    model = Arrivage
    template_name = 'coordinates/arrivage-delete.html'

    def get_success_url(self):
        return reverse('coordinates:arrivages')



class FournisseurCreationView(CreateView):
    model = Fournisseur
    template_name = 'coordinates/fournisseur-create.html'
    fields = ['nom_entreprise', 'contact', 'adresse', 'email']

    def get_success_url(self):
        return reverse('coordinates:fournisseurs-list')

class FournisseurListView(ListView):
    model = Fournisseur
    template_name = 'coordinates/fournisseurs.html'
    context_object_name = 'liste'

class ContactListView(ListView):
    model = Contact
    template_name = 'coordinates/contacts.html'
    context_object_name = 'liste'

class ContactCreationView(CreateView):
    model = Contact
    template_name = 'coordinates/contact-create.html'
    fields = ['nom', 'prenom']

    def get_success_url(self):
        return reverse('coordinates:contacts-list')
