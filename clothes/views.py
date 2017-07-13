from django.shortcuts import reverse
from django.views.generic import ListView, CreateView, FormView
from .models import ClothesCategory, Clothes, ClothesEntry, InventoryClothes
from .forms import ClothesCategoryForm, ClothesForm, InventoryClothesForm
from coordinates.models import Arrivage

# Create your views here.
class ClothesListView(ListView):
    model = Clothes
    template_name = 'clothes/list.html'
    context_object_name = 'clothes'

class ClothesCreationView(CreateView):
    model = Clothes
    form_class = ClothesForm
    template_name = 'clothes/create.html'

    def form_valid(self, form):
        form.save()
        arrivage_id = form['arrivage'].value()
        arrivage = Arrivage.objects.get(pk=arrivage_id)
        ClothesEntry.objects.create(date=arrivage.date,
            article=form.instance,
                                      quantity=form['quantity'].value())
        return super(ClothesCreationView, self).form_valid(form)

    def get_success_url(self):
        return reverse('clothes:clothes-list')

class CategoryCreationView(CreateView):
    model = ClothesCategory
    form_class = ClothesCategoryForm
    template_name = 'clothes/category-create.html'

    def get_success_url(self):
        return reverse('clothes:category-list')

class CategoryListView(ListView):
    model = ClothesCategory
    template_name = 'clothes/category-list.html'
    context_object_name = 'categories'

class InventoryListView(ListView):
    model = InventoryClothes
    template_name = 'clothes/inventory.html'
    context_object_name = 'entries'

class InventoryCreationView(FormView):

    form_class = InventoryClothesForm
    template_name = 'clothes/inventory-create.html'

    def form_valid(self, form):
        form.generate_inventory()
        return super(InventoryCreationView, self).form_valid(form)


    def get_success_url(self):
        return reverse('clothes:inventory')




