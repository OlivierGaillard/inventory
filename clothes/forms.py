from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout
from crispy_forms import layout
from crispy_forms import bootstrap
from django import forms
from django.shortcuts import reverse
from mptt.forms import TreeNodeMultipleChoiceField
from .models import Clothes, ClothesCategory, InventoryClothes
from products.forms import ProductCreateForm, ProductUpdateForm


class ClothesForm(ProductCreateForm):
    categories = TreeNodeMultipleChoiceField(queryset=ClothesCategory.objects.all(), label='Type')

    class Meta(ProductCreateForm.Meta):
        model = Clothes

    def __init__(self, *args, **kwargs):
        super(ClothesForm, self).__init__(*args, **kwargs)
        self.helper.form_action = reverse('clothes:clothes_create')


class ClothesUpdateForm(ProductUpdateForm):

    class Meta(ProductUpdateForm.Meta):
        model = Clothes

    def __init__(self, *args, **kwargs):
        super(ClothesUpdateForm, self).__init__(*args, **kwargs)



class ClothesCategoryForm(forms.ModelForm):

    class Meta:
        model = ClothesCategory
        fields = ['parent', 'title', ]


    def __init__(self, *args, **kwargs):
        super(ClothesCategoryForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'POST'
        self.helper.form_action = reverse('clothes:category_create')
        self.helper.add_input(Submit('submit', 'Submit'))

class AddPhotoForm(forms.Form):
    image   = forms.ImageField()
    legende = forms.CharField(max_length=20)

class CategoryUpdateForm(forms.ModelForm):

    class Meta:
        model = ClothesCategory
        fields = ['parent', 'title']

    def __init__(self, *args, **kwargs):
        super(CategoryUpdateForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'POST'
        self.helper.add_input(Submit('submit', 'Submit'))



class InventoryClothesForm(forms.Form):

    creation_date = forms.DateField(label='Date de création',
                                    widget=forms.TextInput( attrs={ 'type' : 'date' } )
                                    )

    def __init__(self, *args, **kwargs):
        super(InventoryClothesForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-inline'
        self.helper.form_action = "clothes:inventory_create"
        self.helper.form_method = "POST"
        self.helper.add_input(Submit('Submit', 'submit'))

    def generate_inventory(self):
        creation_date = self.cleaned_data['creation_date']
        inventory = InventoryClothes()
        inventory.sum_entries(creation_date)

