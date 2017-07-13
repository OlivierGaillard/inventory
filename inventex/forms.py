from django import forms
from django.forms import ModelForm
from django.shortcuts import reverse
from inventex.models import Article
from finance.models import Currency
from datetime import date

from crispy_forms.helper import FormHelper
from crispy_forms import layout, bootstrap
from crispy_forms.layout import Submit


class ArticleCreateForm(ModelForm):
    quantity = forms.IntegerField(min_value=1, required=True, label="Quantité", initial=0)

    class Meta:
        model = Article
        fields = ('arrivage', 'type_client', 'type_de_produit', 'marque', 'quantity')
        widgets = {
            'type_client' : forms.RadioSelect,
            'type_de_produit' : forms.RadioSelect,
        }

    def __init__(self, *args, **kwargs):
        super(ArticleCreateForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_action = reverse("inventex:article-create")
        self.helper.form_method = "POST"
        self.helper.add_input(Submit('Submit', 'submit'))
        prod_client_layout = layout.Layout(
            layout.Fieldset("Produit et type de client",
                            layout.Field('type_client'),
                            layout.Field('type_de_produit'),
                            )
        )
        self.helper.layout = prod_client_layout


class ArticleUpdateForm(ArticleCreateForm):

    class Meta(ArticleCreateForm.Meta):
        fields = ('arrivage', 'type_de_produit', 'type_client', 'modele',
                  'marque', 'quantity', 'precisions')