import datetime
from django.db import models
from django.utils import timezone
from django.core.validators import RegexValidator



class Pays(models.Model):
    nom  = models.CharField(max_length=80, default='Cameroun')
    code = models.CharField(max_length=4, default='N.D.')
    
    class Meta:
        verbose_name_plural = "Pays"
        unique_together = ('nom', 'code',)
        
    def __str__(self):
        return self.nom + ' (' + self.code + ')'
        

class Localite(models.Model):
    nom  = models.CharField(max_length=80, verbose_name='Lieu', unique=True)
    npa  = models.CharField(max_length=8, null=True, blank=True, verbose_name='NPA',
                            help_text="No postal d'acheminement")
    pays = models.ForeignKey(Pays, null=True)

    def __str__(self):
        if self.npa is None:
            return self.nom
        else:
            return self.npa + ' ' + self.nom

class Adresse(models.Model):
    rue      = models.CharField(max_length=80, null=True, blank=True)
    localite = models.ForeignKey('Localite')
    no       = models.CharField(max_length=8, null=True, blank=True)
    pays     = models.ForeignKey('Pays')
    visavis  = models.CharField(max_length=150, null=True,
                                help_text="Exemple: à côté restaurant Cercle Vert",
                                blank=True)
    expliq   = models.TextField(max_length=200, null=True, blank=True,
                                help_text="Explication supplémentaire.")
    
    def __str__(self):
        return str(self.localite) + '...'

class Phone(models.Model):
    phone_types = [
        ('1', 'Mobile'),
        ('2', 'Bureau'),
        ('3', 'Domicile'),
    ]
    # TODO: adapt the regex to the faker format wich make spaces
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,20}$',
                                 message="Format: '+999999999'. Maximum 20 chiffres.")
    phone_number = models.CharField(max_length=20, validators=[phone_regex], blank=True)
    phone_type  = models.CharField(max_length=10, choices=phone_types, default='1')

    def __str__(self):
        return self.get_phone_type_display() + ' ' + self.phone_number

class ContactPhone(Phone):
    contact = models.ForeignKey('Contact')


class Contact(models.Model):
    prenom    = models.CharField(max_length=80)
    nom       = models.CharField(max_length=80)
    email     = models.EmailField(help_text='Email du contact', null=True, blank=True)

    class Meta:
        ordering = ['nom']
    
    def __str__(self):
        return self.prenom + ' ' + self.nom

    def phones(self):
        return [p for p in self.contactphone_set.all()]

    
class Fournisseur(models.Model):
    nom_entreprise   = models.CharField(max_length=80)
    contact  = models.ForeignKey('Contact', null=True, blank=True)
    adresse  = models.ForeignKey('Adresse', null=True, blank=True)
    email      = models.EmailField(help_text='Email entreprise', null=True, blank=True)
  
    def __str__(self):
        return self.nom_entreprise

    def get_first():
        if Fournisseur.objects.exists():
            return Fournisseur.objects.first()
    
class Arrivage(models.Model):
    """
    Tout article n'est pas nécessairement lié à une date
    d'arrivage, par exemple s'il a été confectionné à l'atelier, mais 
    on peut imaginer que néanmoins il soit renseigné.


    The model does not inherit from "Product" which implies it does
    not have a reference to an enterprise. It should! But it is not cool
    that the user has to choose among a drop-down list of enterprises.

    How can we make this more user-friendly? Simply by filtering the list of
    Arrivage instance with the enterprise the user belongs to, but the user
    will never see the enterprise list.

    """
    date = models.DateField(unique=True, default=timezone.now)
    designation = models.CharField(max_length=30, verbose_name="désignation")
    pays = models.ForeignKey(Pays, blank=True, null=True)
    lieu_provenance = models.ForeignKey(Localite, blank=True, null=True, verbose_name='Localité')
    devise = models.ForeignKey('finance.Currency', null=True, help_text='Devise principale')
    enterprise = models.ForeignKey('products.Enterprise', null=True)
    #fournisseur = models.ForeignKey(Fournisseur, default=Fournisseur.get_first())

    class Meta:
        ordering = ['date']

    # def _get_datestr(self):
    #     return self.date.strftime('%d/%m/%Y')
    
    def __str__(self):
        return self.designation

    def get_total_frais(self):
        """Return the total as a Money instance.
        Using montant.amount would return the number only."""
        total = 0
        for frais in self.fraisarrivage_set.all():
            montant = frais.convert(self.devise.currency_code)
            total += montant
        return total
