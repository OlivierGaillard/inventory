from datetime import datetime
from django.shortcuts import render
from django.urls import reverse
from django import forms
from django.views.generic import CreateView, UpdateView, DetailView, DeleteView, ListView
from django.views.generic.edit import FormView
from django.utils.decorators import method_decorator
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from datetime import date
from .models import Article, Entree, Photo
from .forms import  ArticleCreateForm, ArticleUpdateForm
from finance.models import Achat, Currency
from builtins import KeyError

# Create your views here.

def index(request):
    return render(request, 'index.html')


@method_decorator(login_required, name='dispatch')
class ArticleCreationView(CreateView):
    model = Article
    form_class = ArticleCreateForm
    template_name = 'inventex/article_create.html'


    def form_valid(self, form):
        form.save()
        Entree.objects.create(article=form.instance, quantity=form['quantity'].value())
        return super(ArticleCreationView, self).form_valid(form)

    def get_success_url(self):
        return reverse('inventex:articles-list')

@method_decorator(login_required, name='dispatch')
class ArticlesList(ListView):
    model = Article
    template_name = 'inventex/articles.html'
    context_object_name = 'liste'
    
@method_decorator(login_required, name='dispatch')    
class ArticleDetailView(DetailView):
    model = Article
    fields = ['genre_article', 'modele', 'espece_article', 'sous_espece', 'marque', 'type_de_produit']
    template_name = 'inventex/article_detail.html'
    context_object_name = 'article'


@method_decorator(login_required, name='dispatch')
class ArticleUpdateView(UpdateView):
    model = Article
    form_class = ArticleUpdateForm
    #fields = ['type_de_produit', 'genre_article', 'modele', 'espece_article', 'sous_espece', 'marque']
    template_name = 'inventex/article_update.html'
    context_object_name = 'article'
    #initial = {'quantity': Entree.objects.get(article=self.object.pk).quantity}

    #initial = {'quantity': Entree.objects.get(article=self.object.pk).quantity}

    def get_initial(self):
        previous_quantity = self.object.get_quantity()
        initial = super(ArticleUpdateView, self).get_initial()
        initial['quantity'] = previous_quantity
        return initial

    def form_valid(self, form):
        form.save()
        entree = Entree.objects.get(article=form.instance)
        entree.quantity = form['quantity'].value()
        entree.save()
        return super(ArticleUpdateView, self).form_valid(form)


    def get_success_url(self):
        return reverse('inventex:article-detail', kwargs={'pk': self.object.pk})


@method_decorator(login_required, name='dispatch')    
class ArticleDeleteView(DeleteView):
    model = Article
    fields = ['genre_article']
    template_name = 'inventex/article-delete.html'
    context_object_name = 'article'
    
    def get_success_url(self):
        return reverse('inventex:articles-list')

class EntreesList(ListView):
    model = Entree
    template_name = 'inventex/entrees.html'
    context_object_name = 'liste'