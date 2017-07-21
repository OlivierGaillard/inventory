from django.test import TestCase
from django.core.management import call_command
from django.utils.six import StringIO
from money import Money, xrates
from finance.models import Converter
import pickle
import os
from decimal import Decimal
from money import Money
from .models import Currency

# Create your tests here.
class TestFinance(TestCase):
    
    def setUp(self):        
        self.converter = Converter()


    def test_CHF_EUR(self):
        source = Money(12, 'CHF')
        self.assertAlmostEqual(self.converter.convert(source, 'EUR').amount,
                               Decimal(10.84), 1)

    def test_CHF_AED(self):
        montant = 20.00
        source = Money(montant, 'CHF')
        rate_usd_of_aed = 3.6729
        self.assertAlmostEqual(self.converter.convert(source, 'AED').amount,
                               Decimal(77.25), 1)

    def test_set_rate(self):
        chf = Currency(currency_code='CHF')
        self.assertEqual(1.0, chf.rate_usd)
        chf.set_rate()
        self.assertTrue(1.0 != chf.rate_usd)
        # Calling save will use the Converter to retrieve the rate from file 'rates.txt'


    def btest_get_currencies(self):
        "Web service call to get list all currencies."
        self.converter.get_all_currencies_webservice()

    def test_command_load_currencies(self):
        """Call the following:
        converter.get_rates_webservice() # dump to the pickle file finance/rates.txt
        converter.get_all_currencies_webservice()   # dump to the pickle file finance/currencies.txt
        total = Currency.load_currencies() # Currency factory to create instances with the pickle files.
        """
        chf = Currency.objects.create(currency_code='CHF')
        out = StringIO()
        call_command('load_currencies', sdout=out)

        
        
        
        
