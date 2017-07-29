from django import forms
from crispy_forms.helper import FormHelper, Layout
from crispy_forms.layout import Submit
from .models import FraisArrivage
from finance.models import Currency

class FraisArrivageCreateForm(forms.ModelForm):
    devise_id = forms.ModelChoiceField(queryset=Currency.objects.filter(used=True))

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
    devise_id = forms.ModelChoiceField(queryset=Currency.objects.filter(used=True))

    class Meta:
        model = FraisArrivage
        fields = ['objet', 'date_frais', 'montant', 'devise_id' ]


    def __init__(self, *args, **kwargs):

        super(FraisArrivageUpdateForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'POST'
        self.helper.add_input(Submit('submit', 'Submit'))
