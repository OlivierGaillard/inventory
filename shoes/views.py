from django.shortcuts import reverse, render
from django.http import HttpResponseRedirect
from django.views.generic import ListView, CreateView, FormView, DetailView, DeleteView, UpdateView
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required, permission_required
from finance.models import Achat, Currency
from .models import Shoe, ShoeEntry, ShoeCategory, InventoryShoe, Photo
from .forms import ShoeForm, CategoryForm, InventoryShoeForm, AddPhotoForm, ShoeUpdateForm
from coordinates.models import Arrivage

class ShoeListView(ListView):
    model = Shoe
    template_name = 'shoes/list.html'
    context_object_name = 'shoes'


@method_decorator(login_required, name='dispatch')
class ShoeDeleteView(DeleteView):
    model = Shoe
    template_name = 'shoes/delete.html'
    context_object_name = 'shoe'
    fields = ['name', ]

    def get_success_url(self):
        return reverse('shoes:list')


@method_decorator(login_required, name='dispatch')
class ShoeCreationView(CreateView):
    model = Shoe
    form_class = ShoeForm
    template_name = 'shoes/create.html'


    def form_valid(self, form):
        self.object = form.save()
        arrivage_id = form['arrivage'].value()
        arrivage = Arrivage.objects.get(pk=arrivage_id)
        ShoeEntry.objects.create(date=arrivage.date,
            article=form.instance,
            quantity=form['quantity'].value())
        self.object.update_marque_ref(form['marque'].value(), form['marque_ref'].value())
        return HttpResponseRedirect(self.get_success_url())



@method_decorator(login_required, name='dispatch')
class ShoesDetailView(DetailView):
    model = Shoe
    template_name = 'shoes/detail.html'
    fields = ['arrivage', 'type_client', 'name', 'marque']
    context_object_name = 'shoe'


@method_decorator(login_required, name='dispatch')
class ShoeUpdateView(UpdateView):
    model = Shoe
    form_class = ShoeUpdateForm
    template_name = 'shoes/update.html'
    context_object_name = 'shoe'


    def get_initial(self):
        previous_quantity = self.object.get_quantity()
        initial = super(ShoeUpdateView, self).get_initial()
        initial['quantity'] = previous_quantity
        initial['quantite_achetee'] = previous_quantity # updated below if prix_achat exists.
        initial['categories'] = self.object.categories.last()
        if self.object.marque_ref:
            initial['marque_ref'] = self.object.marque_ref
        else:
            #print('No marque')
            pass
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


    def form_valid(self, form):
        form.save()
        if ShoeEntry.objects.filter(article=form.instance).exists():
            entree = ShoeEntry.objects.get(article=form.instance)
        else:
            entree = ShoeEntry()
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
        return super(ShoeUpdateView, self).form_valid(form)



def upload_pic(request, pk):
    "pk is Shoe ID"
    if request.method == 'POST':
        form = AddPhotoForm(request.POST, request.FILES)
        if form.is_valid():
            shoes = Shoe.objects.get(pk=pk)
            photo = Photo()
            photo.photo = form.cleaned_data['image']
            photo.legende = form.cleaned_data['legende']
            photo.article = shoes
            photo.save()
            return HttpResponseRedirect(reverse('shoes:detail', kwargs={'pk':pk}))
    else:
        shoe = Shoe.objects.get(pk=pk)
        return render(request, "shoes/photo_add.html", {'shoe': shoe})

@method_decorator(login_required, name='dispatch')
class PhotoDeleteView(DeleteView):
    model = Photo
    template_name = 'shoes/photo_delete.html'
    context_object_name = 'image'
    fields = ['legende', 'photo' ]

    def get_success_url(self):
        shoe = self.object.article
        return reverse('shoes:detail', kwargs={'pk':shoe.pk})


@method_decorator(login_required, name='dispatch')
class CategoryCreationView(CreateView):
    model = ShoeCategory
    form_class = CategoryForm
    template_name = 'shoes/category-create.html'

    def get_success_url(self):
        return reverse('shoes:category-list')

class CategoryListView(ListView):
    model = ShoeCategory
    template_name = 'shoes/category-list.html'
    context_object_name = 'categories'

@method_decorator(login_required, name='dispatch')
class InventoryListView(ListView):
    model = InventoryShoe
    template_name = 'shoes/inventory.html'
    context_object_name = 'entries'

@method_decorator(login_required, name='dispatch')
class InventoryCreationView(FormView):
    form_class = InventoryShoeForm
    template_name = 'shoes/inventory-create.html'

    def form_valid(self, form):
        form.generate_inventory()
        return super(InventoryCreationView, self).form_valid(form)


    def get_success_url(self):
        return reverse('shoes:inventory')





