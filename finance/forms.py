from django import forms
from crispy_forms.helper import FormHelper, Layout
from crispy_forms.layout import Submit, Field, Hidden
from crispy_forms.bootstrap import PrependedText
from .models import FraisArrivage
from finance.models import Currency, Vente, ProductType

class CoolCurrencyChoiceField(forms.ModelChoiceField):

    def label_from_instance(self, obj):
        return obj.currency_code + ' : ' + obj.currency_name


class FraisArrivageCreateForm(forms.ModelForm):
    devise_id = CoolCurrencyChoiceField(queryset=Currency.objects.filter(used=True))

    class Meta:
        model = FraisArrivage
        fields = ('arrivage_ref', 'objet', 'date_frais', 'devise_id', 'montant')
        widgets = {
            'date_frais': forms.TextInput(
                attrs={'type': 'date'}
            ),
            'arrivage_ref': forms.TextInput(
                attrs={'type': 'hidden'}
            )
        }

class FraisArrivageFormSetHelper(FormHelper):
    def __init__(self, *args, **kwargs):
        super(FraisArrivageFormSetHelper, self).__init__(*args, **kwargs)
        self.form_method = 'post'
        self.layout = Layout(
            'objet',
            'date_frais',
            'montant',
            'devise_id'
        )

        self.render_required_fields = True

class FraisArrivageUpdateForm(forms.ModelForm):
    devise_id = CoolCurrencyChoiceField(queryset=Currency.objects.filter(used=True))

    class Meta:
        model = FraisArrivage
        fields = ['objet', 'date_frais', 'montant', 'devise_id' ]


    def __init__(self, *args, **kwargs):

        super(FraisArrivageUpdateForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'POST'
        self.helper.add_input(Submit('submit', 'Submit'))

class CurrencyUsageForm(forms.ModelForm):

    class Meta:
        model = Currency
        fields = ['currency_code', 'currency_name', 'used']
        widgets = {
            'currency_code': forms.TextInput(
                attrs={'readonly': 'readonly'}
            ),
            'currency_name': forms.TextInput(
                attrs={'readonly': 'readonly'}
            ),
        }

    def __init__(self, *args, **kwargs):
        super(CurrencyUsageForm,self).__init__(*args, **kwargs)
        self.fields['currency_code'].read_only = True
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-sm-2'
        self.helper.field_class = 'col-sm-3'
        self.helper.form_method = 'POST'
        self.helper.add_input(Submit('submit', 'Submit'))
        self.helper.layout = Layout(
            'currency_code', 'currency_name', 'used',
        )


class VenteCreateForm(forms.ModelForm):
    devise_id = CoolCurrencyChoiceField(queryset=Currency.objects.filter(used=True))

    class Meta:
        model = Vente
        fields = ['product_type', 'product_id', 'quantity', 'montant', 'devise_id', 'client_id', ]
        widgets = {
            'product_type': forms.TextInput(
                attrs={'type': 'disabled'}
            ),
        }

    def __init__(self, *args, **kwargs):
        super(VenteCreateForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-sm-2'
        self.helper.field_class = 'col-sm-3'
        self.helper.form_method = 'POST'
        self.helper.add_input(Submit('submit', 'Submit'))

        self.helper.layout = Layout(
            'client_id', 'product_type'
        )

    def clean_quantity(self):
        q = self.cleaned_data['quantity']
        if q <= 0:
            msg = "Entrez une valeur plus grande que 0 svp."
            raise forms.ValidationError(msg)
        return q

    def clean(self):
        """Check if the quantity does not exceed the available quantity.

        Prio to that I implemented using "clean_quantity" but it failed after I
        changed the fields order in the Meta class.
        For example having ['quantity', 'product_type', 'product_id'] will
        raise a KeyError when 'self.cleaned_data['product_type'] is called.

        For this reason I implement the validation with the "clean" method intended
        to handle multiple fields validation, at the contrary of the field_<field_name>
        method.
        """
        cleaned_data = super(VenteCreateForm,self).clean()
        quantity = cleaned_data.get("quantity", "")
        if len(str(quantity)) > 0:
            quantity = cleaned_data["quantity"]
            product_id = cleaned_data["product_id"]
            product_type = cleaned_data["product_type"]
            product_cls = product_type.get_concrete_class()
            article = product_cls.objects.get(pk=product_id)
            available = article.get_quantity()
            msg = "Quantity %s exceed available stock of %s." % (str(quantity), available)
            if quantity > available:
                raise forms.ValidationError(msg)
        return cleaned_data

class VenteUpdateForm(forms.ModelForm):
    devise_id = CoolCurrencyChoiceField(queryset=Currency.objects.filter(used=True))

    class Meta:
        model = Vente
        fields = ['client_id', 'montant', 'devise_id']

    def __init__(self, *args, **kwargs):
        super(VenteUpdateForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-sm-2'
        self.helper.field_class = 'col-sm-3'
        self.helper.form_method = 'POST'
        self.helper.add_input(Submit('submit', 'Submit'))

    # def clean(self):
    #     """Check if the quantity does not exceed the available quantity.
    #
    #     If it was the last article the quantity may not be greater than one.
    #     If stock was 1 and selling was 1, then the available quantity does not
    #     allow to sell one.
    #
    #
    #     """
    #     cleaned_data = super(VenteUpdateForm,self).clean()
    #     quantity = cleaned_data.get("quantity", "")
    #     if len(str(quantity)) > 0:
    #         quantity     = cleaned_data["quantity"]
    #         product_id   = cleaned_data["product_id"]
    #         product_type = cleaned_data["product_type"]
    #         product_cls  = product_type.get_concrete_class()
    #         article      = product_cls.objects.get(pk=product_id)
    #         available    = article.get_quantity()
    #
    #         msg = "Quantity %s exceed available stock of %s." % (str(quantity), available)
    #         if quantity > available:
    #             raise forms.ValidationError(msg)
    #     return cleaned_data


