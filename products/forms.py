from crispy_forms.helper import FormHelper
from crispy_forms.bootstrap import TabHolder, Tab
from crispy_forms.layout import Submit, Layout
from django import forms
from finance.models import Currency
from finance.forms import CoolCurrencyChoiceField
from .models import Category, Inventory



class ProductCreateForm(forms.ModelForm):
    quantity = forms.IntegerField(min_value=1, required=True, label="Quantité", initial=0)
    marque = forms.CharField(max_length=100, required=False, help_text='Pour entrer une nouvelle marque')

    class Meta:
        abstract = True
        fields = ('type_client', 'marque_ref', 'name', 'quantity', 'arrivage', 'categories')
        widgets = {
            'type_client' : forms.RadioSelect,
        }

    def __init__(self, *args, **kwargs):
        super(ProductCreateForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-4'
        self.helper.layout = Layout(
            TabHolder(
                Tab('Fiche article',
                    'name', 'arrivage', 'quantity'
                    ),
                Tab('Classification',
                    'type_client', 'categories', 'marque_ref', 'marque'
                    ),
            )
        )
        self.helper.form_method = "POST"
        self.helper.add_input(Submit('Submit', 'submit'))

    def clean(self):
        cleaned_data = super(ProductCreateForm, self).clean()
        marque_ref = cleaned_data.get('marque_ref', '')
        if marque_ref is None:
            marque = cleaned_data.get('marque', '')
            if len(marque) == 0:
                msg = "Vous devez choisir une marque ou en créer une en renseignant le champ 'marque'. "
                raise forms.ValidationError(msg)
        return cleaned_data




class ProductUpdateForm(forms.ModelForm):
    marque = forms.CharField(max_length=100, required=False, help_text='Pour entrer une nouvelle marque')
    quantity = forms.IntegerField(min_value=1, required=True, label="Quantité", initial=0)
    montant = forms.DecimalField(max_digits=10, decimal_places=2, required=True,
                                 label="Prix d'achat",
                                 help_text="unitaire ou en gros")
    quantite_achetee = forms.IntegerField(min_value=1, required=True, label="Quantité achetée")
    date_achat = forms.DateField(label="Date d'achat", required=True,
                                  widget=forms.TextInput(attrs={'type': 'date'})
                    )
    devise = CoolCurrencyChoiceField(queryset=Currency.objects.filter(used=True))
    #devise = forms.ModelChoiceField(queryset=Currency.objects.filter(used=True))
    quantite_type = forms.ChoiceField(choices=[(1, "à l'unité"), (2, "en gros")],
                                      widget=forms.RadioSelect(), initial=1,
                                      help_text="Si vous choisissez 'à l'unité' le prix d'achat enregistré sera égal au prix d'achat multiplié par la quantité.",
                                      label="Type d'achat")
    class Meta:
        # model = Accessory / Clothes etc. To be denifed by child class
        abstract = True
        fields = ['categories', 'name', 'type_client', 'marque_ref', 'arrivage', 'devise']

    def __init__(self, *args, **kwargs):
        super(ProductUpdateForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-4'
        self.helper.form_method = 'POST'
        self.helper.add_input(Submit('submit', 'Submit'))
        self.helper.layout = Layout(
            TabHolder(
                Tab('Fiche article',
                     'name', 'arrivage', 'quantity'
                ),
                Tab('Client et marque',
                    'type_client', 'marque_ref', 'marque',
                ),
                Tab('Catégories', 'categories',),
                Tab('Achat',
                    'quantite_type',
                    "quantite_achetee",
                    'montant',
                    'devise',
                    'date_achat',
                ),
            )
        )



    def clean(self):
        """This method is the last validation step. After it the data are copied
        into the model with form.save()"""
        cleaned_data = super(ProductUpdateForm, self).clean()
        marque_ref = cleaned_data.get('marque_ref', '')
        if marque_ref is None:
            marque = cleaned_data.get('marque', '')
            if len(marque) == 0:
                msg = "Vous devez choisir une marque ou en créer une en renseignant le champ 'marque'. "
                raise forms.ValidationError(msg)
        return cleaned_data


class InventoryForm(forms.Form):
    date = forms.TextInput(attrs={'type' : 'date'},)

    class Meta:
        #abstract = True
        fields = ['date',]
        widgets = {
            'date' : forms.TextInput(
                attrs={ 'type' : 'date' }
            ),
        }

