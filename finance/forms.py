from django import forms
from crispy_forms.helper import FormHelper, Layout
from crispy_forms.layout import Submit
from .models import FraisArrivage

class FraisArrivageCreateForm(forms.ModelForm):

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
    class Meta:
        model = FraisArrivage
        fields = ['objet', 'date_frais', 'montant', 'devise_id' ]


    def __init__(self, *args, **kwargs):
        super(FraisArrivageUpdateForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'POST'
        #self.helper.form_action = reverse('finance:list')
        self.helper.add_input(Submit('submit', 'Submit'))
