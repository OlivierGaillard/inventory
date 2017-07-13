from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout
from crispy_forms import layout
from crispy_forms import bootstrap
from django import forms
from django.shortcuts import reverse
from mptt.forms import TreeNodeChoiceField, TreeNodeMultipleChoiceField
from .models import Shoe, InventoryShoe, ShoeCategory
#from products.forms import ProductCreateForm #, InventoryForm


class CategoryForm(forms.ModelForm):

    class Meta:
        model = ShoeCategory
        fields = ['parent', 'title', ]


    def __init__(self, *args, **kwargs):
        super(CategoryForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'POST'
        self.helper.form_action = reverse('shoes:category_create')
        self.helper.add_input(Submit('submit', 'Submit'))


class ShoeForm(forms.ModelForm):
    quantity = forms.IntegerField(min_value=1, required=True, label="Quantité", initial=0)
    categories = TreeNodeMultipleChoiceField(queryset=ShoeCategory.objects.all(), label='Type')

    class Meta:
        model = Shoe
        fields = ('marque_ref','categories', 'name', 'quantity', 'arrivage', 'type_client')
        widgets = {'type_client' : forms.RadioSelect,
        }

    def __init__(self, *args, **kwargs):
        super(ShoeForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-inline'
        self.helper.form_action = reverse('shoes:shoe_create')
        self.helper.form_method = "POST"
        self.helper.add_input(Submit('Submit', 'submit'))



class InventoryShoeForm(forms.Form):

    creation_date = forms.DateField(label='Date de création',
                                    widget=forms.TextInput( attrs={ 'type' : 'date' } )
                                    )

    def __init__(self, *args, **kwargs):
        super(InventoryShoeForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-inline'
        self.helper.form_action = "shoes:inventory_create"
        self.helper.form_method = "POST"
        self.helper.add_input(Submit('Submit', 'submit'))

    def generate_inventory(self):
        creation_date = self.cleaned_data['creation_date']
        inventory = InventoryShoe()
        inventory.sum_entries(creation_date)

