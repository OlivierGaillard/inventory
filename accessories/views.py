from django.conf import settings
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import reverse, render, redirect
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import reverse
from django.views.generic import CreateView, ListView, FormView, DetailView, UpdateView, DeleteView
from .models import Accessory, AccessoryCategory, InventoryAccessory, AccessoryEntry, Photo
from coordinates.models import Arrivage
from finance.models import Achat, Currency
from .forms import AccessoryForm, AccessoryUpdateForm, InventoryAccessoryForm, AccessoryCategoryForm
from .forms import AddPhotoForm, CategoryUpdateForm


@method_decorator(login_required, name='dispatch')
class AccessoryCreationView(CreateView):
    model = Accessory
    form_class = AccessoryForm
    template_name = 'accessories/create.html'

    def form_valid(self, form):
        """This method saves the Accessory instance. """
        self.object = form.save()
        arrivage_id = form['arrivage'].value()
        arrivage = Arrivage.objects.get(pk=arrivage_id)
        AccessoryEntry.objects.create(date=arrivage.date,
            article=form.instance,
            quantity=form['quantity'].value())
        self.object.update_marque_ref(form['marque'].value(), form['marque_ref'].value())
        return HttpResponseRedirect(self.get_success_url())

class AccessoryListView(ListView):
    model = Accessory
    template_name = 'accessories/list.html'
    context_object_name = 'accessoires'

@method_decorator(login_required, name='dispatch')
class AccessoryDetailView(DetailView):
    model = Accessory
    template_name = 'accessories/accessoire.html'
    fields = ['arrivage', 'type_client', 'name', 'marque']
    context_object_name = 'accessory'



@method_decorator(login_required, name='dispatch')
class AccessoryUpdateView(UpdateView):
    model = Accessory
    form_class = AccessoryUpdateForm
    template_name = 'accessories/update.html'
    context_object_name = 'accessory'


    def get_initial(self):
        previous_quantity = self.object.get_quantity()
        initial = super(AccessoryUpdateView, self).get_initial()
        initial['quantity'] = previous_quantity
        initial['quantite_achetee'] = previous_quantity # updated below if prix_achat exists.
        initial['categories'] = self.object.categories.last()
        if self.object.marque_ref:
            initial['marque_ref'] = self.object.marque_ref
        else:
            pass
            #print('No marque')
        initial['marque'] = ''
        if self.object.prix_achat:
            initial['montant'] = self.object.prix_achat.montant
            achat_quantite = self.object.prix_achat.quantite
            initial['quantite_achetee'] = achat_quantite
            initial['date_achat'] = self.object.prix_achat.date_achat
            if achat_quantite == 1:
                initial['quantite_type'] = 1 # achat unitaire
            else:
                initial['quantite_type'] = 2  # achat en gros
        if self.object.arrivage:
            initial['devise'] = self.object.arrivage.devise

        return initial

    # def get_success_url(self):
    #     print("In get_success_url of AccessoryUpdateView")
    #     return reverse('accessories:list')

    def form_valid(self, form):
        form.save()
        if AccessoryEntry.objects.filter(article=form.instance).exists():
            entree = AccessoryEntry.objects.get(article=form.instance)
        else:
            entree = AccessoryEntry()
            entree.article = form.instance
        entree.quantity = form['quantity'].value()

        devise = Currency.objects.get(pk=form['devise'].value())

        montant = float(form['montant'].value())
        montant_total = 0.0
        code_quantite = form['quantite_type'].value()
        if code_quantite == "1":
            montant_total = montant * int(form['quantite_achetee'].value())
        else:
            montant_total = montant

        entree.save()
        achat = Achat.objects.create(montant=montant_total,
                                     quantite=form['quantite_achetee'].value(),
                                     date_achat=form['date_achat'].value(),
                                     devise_id=devise)
        self.object.prix_achat = achat
        self.object.update_marque_ref(marque=form['marque'].value(), marque_ref = form['marque_ref'].value())
        return super(AccessoryUpdateView, self).form_valid(form)


@method_decorator(login_required, name='dispatch')
class AccessoryDeleteView(DeleteView):
    model = Accessory
    template_name = 'accessories/delete.html'
    context_object_name = 'accessory'
    fields = ['name', ]

    def get_success_url(self):
        return reverse('accessories:list')


@method_decorator(login_required, name='dispatch')
class CategoryCreationView(CreateView):
    model = AccessoryCategory
    form_class = AccessoryCategoryForm
    template_name = 'accessories/category-create.html'


class CategoryListView(ListView):
    model = AccessoryCategory
    template_name = 'accessories/category-list.html'
    context_object_name = 'categories'


class CategoryUpdateView(UpdateView):
    model = AccessoryCategory
    template_name = 'accessories/category-update.html'
    context_object_name = 'category'
    form_class = CategoryUpdateForm

    def get_success_url(self):
        return(reverse('accessories:detail', kwargs={'pk': self.object.id}))

@method_decorator(login_required, name='dispatch')
class CategoryDeleteView(DeleteView):
    model = AccessoryCategory
    template_name = 'accessories/category-delete.html'
    fields = ['parent', 'title']

    def get_success_url(self):
        return reverse('accessories:category-list')


@method_decorator(login_required, name='dispatch')
class InventoryListView(ListView):
    model = InventoryAccessory
    template_name = 'accessories/inventory.html'
    context_object_name = 'entries'


@method_decorator(login_required, name='dispatch')
@method_decorator(permission_required('accessories.view_achat', raise_exception=True), name='get')
class InventoryCreationView(FormView):
    form_class = InventoryAccessoryForm
    template_name = 'accessories/inventory-create.html'

    def form_valid(self, form):
        form.generate_inventory()
        return super(InventoryCreationView, self).form_valid(form)


    def get_success_url(self):
        return reverse('accessories:inventory-list')



def upload_pic(request, pk):
    "pk is Accessory ID"
    if request.method == 'POST':
        form = AddPhotoForm(request.POST, request.FILES)
        if form.is_valid():
            accessory = Accessory.objects.get(pk=pk)
            photo = Photo()
            photo.photo = form.cleaned_data['image']
            legende = form.cleaned_data.get('legende', '')
            photo.legende = legende
            photo.article = accessory
            photo.save()
            return HttpResponseRedirect(reverse('accessories:detail', kwargs={'pk':pk}))
        else:
            accessory = Accessory.objects.get(pk=pk)
            return render(request, "accessories/photo_add.html", {'accessory': accessory, 'form': form})

    else:
        accessory = Accessory.objects.get(pk=pk)
        return render(request, "accessories/photo_add.html", {'accessory': accessory})

class PhotoDeleteView(DeleteView):
    model = Photo
    template_name = 'accessories/photo_delete.html'
    context_object_name = 'image'
    fields = ['legende', 'photo' ]

    def get_success_url(self):
        accessory = self.object.article
        return reverse('accessories:detail', kwargs={'pk':accessory.pk})






