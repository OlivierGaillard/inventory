from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout
from crispy_forms.bootstrap import TabHolder, Tab
from django import forms
from django.shortcuts import reverse
from mptt.forms import TreeNodeMultipleChoiceField
from finance.models import Currency
from .models import Accessory, InventoryAccessory, AccessoryCategory
from products.forms import ProductCreateForm, ProductUpdateForm


class AccessoryForm(ProductCreateForm):
    #categories = TreeNodeMultipleChoiceField(queryset=AccessoryCategory.objects.all(), label='Type')
    quantity = forms.IntegerField(min_value=1, required=True, label="Quantité", initial=0)

    class Meta(ProductCreateForm.Meta):
        model = Accessory

    def __init__(self, *args, **kwargs):
        super(AccessoryForm, self).__init__(*args, **kwargs)
        self.helper.form_action = reverse('accessories:create')

class AccessoryUpdateForm(ProductUpdateForm):

    class Meta(ProductUpdateForm.Meta):
        model = Accessory

    def __init__(self, *args, **kwargs):
        super(AccessoryUpdateForm, self).__init__(*args, **kwargs)

class CategoryUpdateForm(forms.ModelForm):

    class Meta:
        model = AccessoryCategory
        fields = ['parent', 'title']

    def __init__(self, *args, **kwargs):
        super(CategoryUpdateForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'POST'
        self.helper.add_input(Submit('submit', 'Submit'))


class AddPhotoForm(forms.Form):
    image   = forms.ImageField()
    legende = forms.CharField(max_length=20)   #models.CharField(max_length=20, blank=True, null=True)
 #models.ForeignKey(Accessory, blank=True, null=True)



class AccessoryCategoryForm(forms.ModelForm):
    #quantity = forms.IntegerField(min_value=1, required=True, label="Quantité", initial=0)
    class Meta:
        model = AccessoryCategory
        fields = ['parent', 'title', ]


    def __init__(self, *args, **kwargs):
        super(AccessoryCategoryForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'POST'
        self.helper.form_action = reverse('accessories:category-create')
        self.helper.add_input(Submit('submit', 'Submit'))


class InventoryAccessoryForm(forms.Form):

    # class Meta(InventoryForm.Meta):
    #      fields = ['date']

    #creation_date = forms.TextInput(attrs={'type' : 'date'}, label='Date de création')
    creation_date = forms.DateField(label='Date de création',
                                    widget=forms.TextInput( attrs={ 'type' : 'date' } )
                                    )

    def __init__(self, *args, **kwargs):
        super(InventoryAccessoryForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-inline'
        self.helper.form_action = "accessories:inventory-create"
        self.helper.form_method = "POST"
        self.helper.add_input(Submit('Submit', 'submit'))

    def generate_inventory(self):
        creation_date = self.cleaned_data['creation_date']
        inventory = InventoryAccessory()
        inventory.sum_entries(creation_date)

