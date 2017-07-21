from django.test import TestCase
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
                               Decimal(10.9690), 1)

    def test_CHF_AED(self):
        montant = 20.00
        source = Money(montant, 'CHF')
        rate_usd_of_aed = 3.6729
        self.assertAlmostEqual(self.converter.convert(source, 'AED').amount,
                               Decimal(73.6), 1)

    def test_set_rate(self):
        chf = Currency(currency_code='CHF')
        self.assertEqual(1.0, chf.rate_usd)
        chf.set_rate()
        self.assertTrue(1.0 != chf.rate_usd)
        # Calling save will use the Converter to retrieve the rate from file 'rates.txt'


    def gtest_get_rates_webservice(self):
        self.converter.get_rates_webservice()
        print (self.converter.last_modified)
        self.assertEqual(self.converter.update_status, 'updated')


        
        
        
        
