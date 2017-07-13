from django.shortcuts import reverse
from django.views.generic import ListView, CreateView, FormView
from .models import Shoe, ShoeEntry, ShoeCategory, InventoryShoe
from .forms import ShoeForm, CategoryForm, InventoryShoeForm
from coordinates.models import Arrivage

class ShoeListView(ListView):
    model = Shoe
    template_name = 'shoes/list.html'
    context_object_name = 'shoes'

class ShoeCreationView(CreateView):
    model = Shoe
    form_class = ShoeForm
    template_name = 'shoes/create.html'

    # def get_initial(self):
    #     filtered_categories = Category.objects.filter()
    #     initial = super(ArticleUpdateView, self).get_initial()
    #     initial['quantity'] = previous_quantity
    #     return initial

    def form_valid(self, form):
        form.save()
        arrivage_id = form['arrivage'].value()
        arrivage = Arrivage.objects.get(pk=arrivage_id)
        ShoeEntry.objects.create(date=arrivage.date,
            article=form.instance,
                                      quantity=form['quantity'].value())
        return super(ShoeCreationView, self).form_valid(form)

    def get_success_url(self):
        return reverse('shoes:shoe-list')

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

class InventoryListView(ListView):
    model = InventoryShoe
    template_name = 'shoes/inventory.html'
    context_object_name = 'entries'


class InventoryCreationView(FormView):
    form_class = InventoryShoeForm
    template_name = 'shoes/inventory-create.html'

    def form_valid(self, form):
        form.generate_inventory()
        return super(InventoryCreationView, self).form_valid(form)


    def get_success_url(self):
        return reverse('shoes:inventory')





