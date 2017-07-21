from django.db import models
from django.utils import timezone
from _locale import CODESET
from money import Money, xrates
import pickle
from decimal import Decimal
import requests
import json
from django.utils import timezone  
from django.conf import settings
import os

    
class Converter():
    """ 'source' is one instance of 'Montant' and 'target'
         is an instance of 'Devise'.
    """
    
    def __init__(self):
        rates_file = os.path.join(settings.BASE_DIR, settings.CURRENCY_RATES_FILE)
#         with open('./finance/rates.txt', 'rb') as f:
        with open(rates_file, 'rb') as f:
            self.rates = pickle.load(f)
        xrates.install('money.exchange.SimpleBackend')
        self.update_status = 'not updated'
        self.last_modified = ''
        
    
    def convert(self, money_source, code_target):
        """ 'source' is a Money instance and
        'target' a money code (CHF, EUR).
        """
        xrates.base = 'USD'
        xrates.setrate(money_source.currency,
                       Decimal(self.rates[money_source.currency]))
        xrates.setrate(code_target,
                       Decimal(self.rates[code_target]))
        return money_source.to(code_target)
    
    def get_rates_webservice(self):
        udpate_status = 'NOK'
        id = settings.CURRENCYSERVICE_ID
        url = 'https://openexchangerates.org/api/latest.json'
        param = {'app_id' : id}
        r = requests.get(url, params=param)
        if r.status_code == 200:
            self.last_modified = r.headers['Last-Modified']
            rates = r.json()['rates']
            with open('./finance/rates.txt', 'wb') as outfile:
                pickle.dump(rates, outfile)
                self.update_status = 'updated'
      
    def get_rate(self, currency_code):
        """ Returns a Decimal for the rate.
        """  
        return Decimal(self.rates[currency_code])  
    
        
class Currency(models.Model):
    currency_code   = models.CharField(max_length=3, unique=True)
    rate_usd        = models.DecimalField(max_digits=15, decimal_places=4, 
                                          default=1.0, 
                                          editable=False)
    last_update     = models.DateField(auto_now=True)
    
    def set_rate(self):
        converter = Converter()
        try:
            self.rate_usd = converter.get_rate(self.currency_code)
        except KeyError:
            err_msg = "Code monnaie %s inconnu." % self.currency_code
            raise KeyError(BaseException, err_msg)
        
    def save(self, *args, **kwargs):
        self.set_rate()
        super(Currency, self).save(*args, **kwargs) # Call the "real" save() method.

    def __str__(self):
        return self.currency_code + ': ' + str(self.rate_usd) + (' (USD)')

    class Meta:
        verbose_name_plural = "Currencies"
    
    
class Achat(models.Model):
    montant     = models.DecimalField(max_digits=10, decimal_places=2  )
    objet       = models.CharField(max_length=80, null=True)
    quantite    = models.IntegerField()
    date_achat  = models.DateField()
    devise_id   = models.ForeignKey('Currency', default=1)
    
    def __str__(self):
        return str(self.montant) + ' ' + self.devise_id.currency_code



class FraisType(models.Model):
    nom = models.CharField(max_length=80)
    
    def __str__(self):
        return self.nom

class Frais(models.Model):
    montant     = models.DecimalField(max_digits=10, decimal_places=2  )
    objet       = models.CharField(max_length=80, default='')
    date_frais  = models.DateField(default=timezone.now)
    frais_type  = models.ForeignKey(FraisType, null=True, blank=True)
    devise_id   = models.ForeignKey(Currency, null=True)
    
    def __str__(self):
        return str(self.date_frais) + ' / ' +  self.objet + ' ' + str(self.montant)

    class Meta:
        verbose_name_plural = "Frais"
        abstract = True
        #ordering = ['date_frais']

    def convert(self, target_currency_code):
        converter = Converter()
        montant_source = Money(self.montant, self.devise_id.currency_code)
        return converter.convert(montant_source, target_currency_code )
        
        
class FraisArrivage(Frais):
    arrivage_ref = models.ForeignKey('coordinates.Arrivage', null=True)

    class Meta:
        ordering = ['arrivage_ref', '-date_frais']
        
class Tarif(models.Model):
    achat = models.ForeignKey(Achat, null=True, blank=True)
    prix_vente_min = models.DecimalField(max_digits=10, decimal_places=2  )
    
    def __str__(self):
        return str(self.prix_vente_min)
        
    




