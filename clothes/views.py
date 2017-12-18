from django.shortcuts import reverse, render
from django.http import HttpResponseRedirect, HttpResponse
from django.views.generic import ListView, CreateView, FormView, DetailView, UpdateView, DeleteView
from .models import ClothesCategory, Clothes, ClothesEntry, InventoryClothes, Photo
from .forms import ClothesCategoryForm, ClothesForm, ClothesUpdateForm, AddPhotoForm, InventoryClothesForm, CategoryUpdateForm
from coordinates.models import Arrivage
from finance.models import Achat, Currency
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required, permission_required
from products.models import Employee
from django.contrib.auth.mixins import UserPassesTestMixin
from django_filters import FilterSet, CharFilter
from django_filters.views import FilterView


class ArticleFilter(FilterSet):
    arrivage__designation = CharFilter(lookup_expr='icontains')
    class Meta:
        model = Clothes
        fields = {'id' : ['exact'],
                  'name' : ['icontains'],
                  }

    @property
    def qs(self):
        parent = super(ArticleFilter, self).qs
        enterprise_of_current_user = Employee.get_enterprise_of_current_user(self.request.user)
        return parent.filter(product_owner=enterprise_of_current_user)


@method_decorator(login_required, name='dispatch')
class ArticleFilteredView(UserPassesTestMixin, FilterView):
    filterset_class = ArticleFilter
    template_name = 'clothes/flist.html' # filtered list
    context_object_name = 'clothes'

    def test_func(self):
        return  Employee.is_current_user_employee(self.request.user)

    def get_context_data(self, **kwargs):
        context = super(ArticleFilteredView, self).get_context_data(**kwargs)
        enterprise_of_current_user = Employee.get_enterprise_of_current_user(self.request.user)
        context['enterprise'] = enterprise_of_current_user
        return context


@method_decorator(login_required, name='dispatch')
class ClothesCreationView(CreateView):
    model = Clothes
    form_class = ClothesForm
    template_name = 'clothes/create.html'

    def form_valid(self, form):
        self.object = form.save()
        arrivage_id = form['arrivage'].value()
        arrivage = Arrivage.objects.get(pk=arrivage_id)
        ClothesEntry.objects.create(date=arrivage.date,
            article=form.instance,
            quantity=form['quantity'].value())
        self.object.update_marque_ref(form['marque'].value(), form['marque_ref'].value())
        return HttpResponseRedirect(self.get_success_url())

    def get_form_kwargs(self):
        kwargs = super(ClothesCreationView, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs




@method_decorator(login_required, name='dispatch')
class ClothesDetailView(DetailView):
    model = Clothes
    template_name = 'clothes/detail.html'
    fields = ['arrivage', 'type_client', 'name', 'marque']
    context_object_name = 'cloth'



@method_decorator(login_required, name='dispatch')
class ClothesUpdateView(UpdateView):
    model = Clothes
    form_class = ClothesUpdateForm
    template_name = 'clothes/update.html'
    context_object_name = 'cloth'


    def get_initial(self):
        previous_quantity = self.object.get_quantity()
        initial = super(ClothesUpdateView, self).get_initial()
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
        if ClothesEntry.objects.filter(article=form.instance).exists():
            entree = ClothesEntry.objects.get(article=form.instance)
        else:
            entree = ClothesEntry()
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
        return super(ClothesUpdateView, self).form_valid(form)

def upload_pic(request, pk):
    "pk is Clothes ID"
    if request.method == 'POST':
        form = AddPhotoForm(request.POST, request.FILES)
        if form.is_valid():
            clothes = Clothes.objects.get(pk=pk)
            photo = Photo()
            photo.photo = form.cleaned_data['image']
            legende = form.cleaned_data.get('legende', '')
            photo.legende = legende
            photo.article = clothes
            photo.save()
            return HttpResponseRedirect(reverse('clothes:detail', kwargs={'pk':pk}))
        else:
#            print(form.errors)
            clothes = Clothes.objects.get(pk=pk)
            return render(request, "clothes/photo_add.html", {'cloth': clothes, 'form':form})

    else:
        clothes = Clothes.objects.get(pk=pk)
        return render(request, "clothes/photo_add.html", {'cloth': clothes})

class PhotoDeleteView(DeleteView):
    model = Photo
    template_name = 'clothes/photo_delete.html'
    context_object_name = 'image'
    fields = ['legende', 'photo' ]

    def get_success_url(self):
        cloth = self.object.article
        return reverse('clothes:detail', kwargs={'pk':cloth.pk})



@method_decorator(login_required, name='dispatch')
class ClothesDeleteView(DeleteView):
    model = Clothes
    template_name = 'clothes/delete.html'
    context_object_name = 'cloth'
    fields = ['name', ]

    def get_success_url(self):
        return reverse('clothes:list')

@method_decorator(login_required, name='dispatch')
class CategoryCreationView(CreateView):
    model = ClothesCategory
    form_class = ClothesCategoryForm
    template_name = 'clothes/category-create.html'


class CategoryUpdateView(UpdateView):
    model = ClothesCategory
    template_name = 'clothes/category-update.html'
    context_object_name = 'category'
    form_class = CategoryUpdateForm


@method_decorator(login_required, name='dispatch')
class CategoryDeleteView(DeleteView):
    model = ClothesCategory
    template_name = 'clothes/category-delete.html'
    fields = ['parent', 'title']

    def get_success_url(self):
        return reverse('clothes:category-list')


class CategoryListView(ListView):
    model = ClothesCategory
    template_name = 'clothes/category-list.html'
    context_object_name = 'categories'

@method_decorator(login_required, name='dispatch')
class InventoryListView(ListView):
    model = InventoryClothes
    template_name = 'clothes/inventory.html'
    context_object_name = 'entries'

    def get_queryset(self):
        enterprise_of_current_user = Employee.get_enterprise_of_current_user(self.request.user)
        return InventoryClothes.objects.filter(article__product_owner=enterprise_of_current_user)


@method_decorator(login_required, name='dispatch')
class InventoryCreationView(FormView):

    form_class = InventoryClothesForm
    template_name = 'clothes/inventory-create.html'

    def form_valid(self, form):
        enterprise_of_current_user = Employee.get_enterprise_of_current_user(self.request.user)
        form.generate_inventory(enterprise_of_current_user)
        return super(InventoryCreationView, self).form_valid(form)


    def get_success_url(self):
        return reverse('clothes:inventory')




