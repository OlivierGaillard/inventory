
from django.http import HttpResponseRedirect
from django.views.generic import CreateView, UpdateView, DetailView, DeleteView, ListView
from django.shortcuts import render
from django.urls import reverse
from django import forms
from django.contrib.auth.decorators import permission_required, login_required
from django.utils.decorators import method_decorator

from finance.models import Currency, FraisArrivage
from coordinates.models import Pays
from .models import Arrivage, Fournisseur, Contact, Localite
from .forms import ArrivageCreateForm, ArrivageUpdateForm, LocaliteCreateForm, LocaliteUpdateForm

class LocationListView(ListView):
    model = Localite
    template_name = 'coordinates/locations.html'
    context_object_name = 'locations'

class LocationCreationView(CreateView):
    model = Localite
    form_class = LocaliteCreateForm
    template_name = 'coordinates/location-create.html'

    def get_success_url(self):
        return reverse('coordinates:locations')

class LocationUpdateView(UpdateView):
    model = Localite
    form_class = LocaliteUpdateForm
    template_name = 'coordinates/location-update.html'
    context_object_name = 'location'

    def get_success_url(self):
        return reverse('coordinates:locations')

class LocationDeleteView(DeleteView):
    model = Localite
    template_name = 'coordinates/location-delete.html'
    context_object_name = 'location'

    def get_success_url(self):
        return reverse('coordinates:locations')

@method_decorator(login_required, name='dispatch')
@method_decorator(permission_required('accessories.view_achat', raise_exception=True), name='dispatch')
class ArrivageCreationView(CreateView):
    model = Arrivage
    template_name = 'coordinates/arrivage-create.html'
    form_class = ArrivageCreateForm

    def get_initial(self):
        initial = super(ArrivageCreationView, self).get_initial()
        initial['devise'] = Currency.objects.first()
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
