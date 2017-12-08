import sys
from django import forms
from django.shortcuts import reverse
from crispy_forms.helper import FormHelper
from crispy_forms.bootstrap import TabHolder, Tab, Accordion, AccordionGroup
from crispy_forms.layout import Submit, Layout, HTML
from finance.models import Currency, FraisArrivage
from finance.forms import CoolCurrencyChoiceField
from .models import Arrivage, Localite, Pays
from products.models import Enterprise

class LocaliteCreateForm(forms.ModelForm):

    class Meta:
        model = Localite
        fields = ['nom', 'npa', 'pays']

    def __init__(self, *args, **kwargs):
        super(LocaliteCreateForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-sm-1'
        self.helper.field_class = 'col-sm-4'
        self.helper.form_method = 'POST'
        self.helper.layout = Layout(
            'nom', 'npa', 'pays',
            Submit('submit', 'Submit'),
        )
        self.helper.form_action = reverse('coordinates:location-create')


class LocaliteUpdateForm(forms.ModelForm):

    class Meta:
        model = Localite
        fields = ['nom', 'npa', 'pays']

    def __init__(self, *args, **kwargs):
        super(LocaliteUpdateForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-sm-1'
        self.helper.field_class = 'col-sm-4'
        self.helper.form_method = 'POST'
        self.helper.layout = Layout(
            'nom', 'npa', 'pays',
            Submit('submit', 'Submit'),
        )


class CoolEnterpriseChoiceField(forms.ModelChoiceField):

    def label_from_instance(self, obj):
        return obj.name


class ArrivageCreateForm(forms.ModelForm):
    devise = CoolCurrencyChoiceField(queryset=Currency.objects.filter(used=True))
    enterprise = CoolEnterpriseChoiceField(queryset=Enterprise.objects.all(), disabled=True, required=False)

    class Meta:
        model = Arrivage
        fields = ('date', 'designation', 'devise', 'enterprise')
        widgets = {
            'date': forms.TextInput(
                attrs={'type': 'date'}
            ),
        }


# class CoolCurrencyChoiceField(forms.ModelChoiceField):
#
#     def label_from_instance(self, obj):
#         return obj.currency_code + ' : ' + obj.currency_name

class ArrivageUpdateForm(ArrivageCreateForm):
    nouveau_pays = forms.CharField(max_length=100, required=False, help_text='Pour entrer un nouveau pays')
    code_pays    = forms.CharField(max_length=4, required=False,
                                   help_text="Pour entrer le code d'un nouveau pays. Valeur par défaut Non Déterminée.",
                                   initial="N.D.")
    devise = CoolCurrencyChoiceField(queryset=Currency.objects.filter(used=True))
    nouveau_lieu = forms.CharField(max_length=100, required=False, label="Locatité", help_text='Pour entrer un nouveau lieu')
    nouveau_lieu_npa = forms.CharField(max_length=8, required=False, label="NPA",
                                       help_text="No postal d'acheminement. Laisser vide si inconnu.")
    #devise = forms.ModelChoiceField(queryset=)

    def __init__(self, *args, **kwargs):
        super(ArrivageUpdateForm,self).__init__(*args, **kwargs)
        self.fields['pays'].required = False
        self.fields['lieu_provenance'].required = False
        self.fields['devise'].required = True
        arrivage = kwargs.get('instance')
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-sm-2'
        self.helper.field_class = 'col-sm-3'
        self.helper.form_method = 'POST'
        self.helper.add_input(Submit('submit', 'Submit'))
        self.helper.layout = Layout(
            TabHolder(
                Tab('Date, désignation et devise',
                    'date', 'designation', 'devise',
                ),
                Tab('Provenance',
                    'pays', 'lieu_provenance',
                ),

                Tab('Ajouter un pays, un lieu',
                    Accordion(
                        AccordionGroup('Ajouter un pays',
                          'nouveau_pays',
                          'code_pays', active=False
                        ),
                        AccordionGroup('Ajouter un lieu',
                              'nouveau_lieu', 'nouveau_lieu_npa'
                        ),
                    )
                ),

                Tab('Saisir des frais',
                  HTML("""
                  <p>Veuilley suivre ce <a href="{% url "finance:add_frais" arrivage.pk %}">lien</a> pour ajouter des frais.</p>
                  """),
                ),
            )
        )



    class Meta(ArrivageCreateForm.Meta):
        fields = ('date', 'designation', 'devise', 'enterprise', 'pays', 'lieu_provenance',)

    def update_land(self, cleaned_data):
        pays_ref = cleaned_data.get('pays', '')
        new_land = cleaned_data.get('nouveau_pays', '')

        if not pays_ref and not new_land:
            raise forms.ValidationError("Remplir le champ 'Nouveau_pays' si aucun pays de la liste n'est selectionne.")
        elif new_land:
            code_pays = cleaned_data.get('code_pays', 'N.D.')
            if Pays.objects.filter(nom=new_land).count() == 0:
                pays = Pays.objects.create(nom=new_land, code=code_pays)
                cleaned_data['pays'] = pays
            else:
                raise forms.ValidationError("Le pays %s existe déjà." % new_land)
        elif pays_ref:
            pass
        else:
            raise forms.ValidationError("Erreur imprévue: %s" % forms.errors.as_data())
        return cleaned_data

    def update_location(self, cleaned_data):
        lieu_selected = cleaned_data.get('lieu_provenance', '')
        new_location  = cleaned_data.get('nouveau_lieu', '')
        if not lieu_selected and not new_location:
            raise forms.ValidationError("Remplir le champ 'Nouveau_lieu' si aucun lieu de la liste n'est selectionné.")
        elif new_location:
            pays_ref = cleaned_data.get('pays')
            npa = cleaned_data.get('nouveau_lieu_npa')
            if not pays_ref:
                location = Localite.objects.create(nom=new_location)
            elif npa:
                location = Localite.objects.create(nom=new_location, npa=npa, pays=pays_ref)
            else:
                location = Localite.objects.create(nom=new_location)
            cleaned_data['lieu_provenance'] = location
        elif lieu_selected:
            cleaned_data['lieu_provenance'] = lieu_selected
        else:
            raise forms.ValidationError("Erreur imprévue: %s" % self.errors.as_data())
        return cleaned_data



    def clean(self):
        cleaned_data = super(ArrivageUpdateForm, self).clean()
        cleaned_data = self.update_land(cleaned_data)
        cleaned_data = self.update_location(cleaned_data)
        return cleaned_data


