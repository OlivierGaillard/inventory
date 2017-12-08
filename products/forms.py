from crispy_forms.helper import FormHelper
from crispy_forms.bootstrap import TabHolder, Tab
from crispy_forms.layout import Submit, Layout
from django import forms
from finance.models import Currency
from finance.forms import CoolCurrencyChoiceField
from .models import Category, Inventory, Employee, Enterprise
from coordinates.models import Arrivage


class ProductCreateForm(forms.ModelForm):
    """
    One word about the mechanic here.

    This abstract is inherited by every article: Clothes, Shoe and Accessory.

    The form defines the attribute *user* which will be set by the CreationViews' method
    *get_form_kwargs*. Once set by the view it is used by its *init* method to
    filter the queryset of the fields 'arrivage' and 'product_owner' by the enterprise
    to which the user belongs to (if it is an employee, which she should be).

    """
    quantity = forms.IntegerField(min_value=1, required=True, label="Quantité", initial=0,
                                  help_text="Quantité en stock (peut différer de la quantité achetée)")
    marque = forms.CharField(max_length=100, required=False, help_text='Pour entrer une nouvelle marque')

    class Meta:
        abstract = True
        fields = ('type_client', 'marque_ref', 'name', 'quantity', 'arrivage', 'product_owner', 'categories')
        widgets = {
            'type_client' : forms.RadioSelect,
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(ProductCreateForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-4'
        self.helper.layout = Layout(
            TabHolder(
                Tab('Fiche article',
                    'name', 'arrivage', 'product_owner', 'quantity'
                    ),
                Tab('Classification',
                    'type_client', 'categories', 'marque_ref', 'marque'
                    ),
            )
        )
        self.helper.form_method = "POST"
        self.helper.add_input(Submit('Submit', 'submit'))
        if self.user:
            user_enterprise = Employee.get_enterprise_of_current_user(self.user)
            self.fields['arrivage'].queryset = Arrivage.objects.filter(enterprise=user_enterprise)
            self.fields['product_owner'].queryset = Enterprise.objects.filter(pk=user_enterprise.pk)

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

