import sys
from django import forms
from django.shortcuts import reverse
from crispy_forms.helper import FormHelper
from crispy_forms.bootstrap import TabHolder, Tab, Accordion, AccordionGroup
from crispy_forms.layout import Submit, Layout, HTML
from finance.models import Currency, FraisArrivage
from .models import Arrivage, Localite, Pays

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


class ArrivageCreateForm(forms.ModelForm):

    class Meta:
        model = Arrivage
        fields = ('date', 'designation', 'devise',)
        widgets = {
            'date': forms.TextInput(
                attrs={'type': 'date'}
            ),
        }



class ArrivageUpdateForm(ArrivageCreateForm):
    nouveau_pays = forms.CharField(max_length=100, required=False, help_text='Pour entrer un nouveau pays')
    code_pays    = forms.CharField(max_length=4, required=False,
                                   help_text="Pour entrer le code d'un nouveau pays. Valeur par défaut Non Déterminée.",
                                   initial="N.D.")
    devise = forms.ModelChoiceField(queryset=Currency.objects.filter(used=True), to_field_name="currency_name")
    nouvelle_devise = forms.CharField(max_length=5, required=False, help_text="Entrez le code (CHF, EUR) de la nouvelle devise.")
    nouveau_lieu = forms.CharField(max_length=100, required=False, label="Locatité", help_text='Pour entrer un nouveau lieu')
    nouveau_lieu_npa = forms.CharField(max_length=8, required=False, label="NPA",
                                       help_text="No postal d'acheminement. Laisser vide si inconnu.")
    # Frais: may be filled afterwards on later stage
    # frais_objet = forms.CharField(max_length=80, required=False)
    # frais_montant = forms.DecimalField(max_digits=10, decimal_places=2, required=False)
    # frais_devise  = forms.ModelChoiceField(queryset=Currency.objects.all(), required=False)

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
                    'date', 'designation', 'devise'
                ),
                Tab('Provenance',
                    'pays', 'lieu_provenance',
                ),

                Tab('Ajouter un pays, un lieu ou une devise',
                    Accordion(
                        AccordionGroup('Ajouter un pays',
                          'nouveau_pays',
                          'code_pays', active=False
                        ),
                        AccordionGroup('Ajouter un lieu',
                              'nouveau_lieu', 'nouveau_lieu_npa'
                        ),
                        AccordionGroup('Ajouter une devise',
                          'nouvelle_devise',
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
        fields = ('date', 'designation', 'devise', 'pays', 'lieu_provenance',)

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

    def update_currency(self, cleaned_data):
        new_code = cleaned_data.get('nouvelle_devise', '')
        if new_code:
            if Currency.objects.filter(currency_code=new_code).count() == 0:
                try:
                    new_currency = Currency.objects.create(currency_code=new_code)
                    cleaned_data['devise'] = new_currency
                except:
                    msg = "Erreur lors de la création de la devise '%s'." % new_code
                    msg += "Erreur: %s " % sys.exc_info()[0]
                    raise forms.ValidationError(msg)
            else:
                raise forms.ValidationError("La devise '%s' existe déjà!" % new_code)
        return cleaned_data



    def clean(self):
        cleaned_data = super(ArrivageUpdateForm, self).clean()
        cleaned_data = self.update_land(cleaned_data)
        cleaned_data = self.update_location(cleaned_data)
        cleaned_data = self.update_currency(cleaned_data)
        #cleaned_data = self.update_frais(cleaned_data)
        return cleaned_data


