from django.test import TestCase
from django.http import HttpRequest
from django.shortcuts import reverse
from django.test import TestCase, Client
from datetime import date
from finance.models import Currency, FraisArrivage, FraisType
from accessories.models import Accessory, AccessoryMarque, AccessoryCategory, AccessoryEntry, AccessoryOutput, InventoryAccessory
from coordinates.models import Arrivage, Pays, Localite
from coordinates.forms import ArrivageCreateForm, ArrivageUpdateForm



class TestFraisArrivage(TestCase):

    def setUp(self):
        self.start_date = date(year=2017, month=1, day=1)
        cat1 = AccessoryCategory.objects.create(parent=None, title='Valises et sacoches')
        self.cat2 = AccessoryCategory.objects.create(parent=cat1, title='Valises')
        cat3 = AccessoryCategory.objects.create(parent=cat1, title='Sacoches')


        # These ones are used to test create and update forms and views.
        self.cat = AccessoryCategory(parent=self.cat2, title='boum')
        self.cat.save()
        self.arrivage = Arrivage(date=date(2017, 2, 1), designation='Arrivage-1')
        self.arrivage.save()

        self.ch = Pays.objects.create(nom='Suisse', code='CH')
        self.chf = Currency.objects.create(currency_code='CHF', rate_usd=0.9981)
        self.hublot = AccessoryMarque.objects.create(nom_marque = 'Hublot')
        self.constant = AccessoryMarque.objects.create(nom_marque = 'Constant')

        self.frais_type_transport = FraisType.objects.create(nom='transport')
        self.frais_type_repas = FraisType.objects.create(nom='repas')

        self.location_lausanne = Localite.objects.create(nom='Lausanne')

    def test_createFraisArrivage(self):
        frais_arrivage = FraisArrivage(arrivage_ref=self.arrivage)
        frais_arrivage.devise_id = self.chf
        frais_arrivage.montant = 1200.00
        frais_arrivage.objet = 'Vol Yaounde-Zurich'
        frais_arrivage.frais_type = self.frais_type_transport
        frais_arrivage.save()
        frais_arrivage2 = FraisArrivage(arrivage_ref=self.arrivage)
        frais_arrivage2.devise_id = self.chf
        frais_arrivage2.montant = 120.00
        frais_arrivage2.objet = 'train'
        frais_arrivage2.frais_type = self.frais_type_transport
        frais_arrivage2.save()
        # Obtenir les frais d'un arrivage
        frais_count = self.arrivage.fraisarrivage_set.count()
        self.assertEqual(2, frais_count)
        frais_count = FraisArrivage.objects.filter(arrivage_ref = self.arrivage).count()
        self.assertEqual(2, frais_count)

        # To add Frais to one arrivage
        frais_arrivage3 = FraisArrivage()
        frais_arrivage3.devise_id = self.chf
        frais_arrivage3.montant = 15.00
        frais_arrivage3.objet = 'repas'
        frais_arrivage3.frais_type = self.frais_type_repas
        frais_arrivage3.save()
        self.arrivage.fraisarrivage_set.add(frais_arrivage3)
        frais_count = self.arrivage.fraisarrivage_set.count()
        self.assertEqual(3, frais_count)

    def test_ArrivageCreateForm(self):
        """New fields 'nouveau_pays'et 'nouveau_lieu' permettent de rajouter
          ces instances de coordinates.Pays et coordinates.Localite"""
        data = {'date' : date(2017, 3, 1),
                'designation' :'Arrivage-1',
                'devise' : self.chf.id}
        form = ArrivageCreateForm(data)
        self.assertTrue(form.is_valid(), form.errors.as_data())

    def test_ArrivageUpdateForm_failed(self):
        """New fields 'nouveau_pays'et 'nouveau_lieu' permettent de rajouter
          ces instances de coordinates.Pays et coordinates.Localite"""
        data = {'date': date(2017, 3, 1),
                'designation': 'Arrivage-1',
                'devise': self.chf.id}
        form = ArrivageUpdateForm(data)
        self.assertFalse(form.is_valid(), form.errors.as_data())

    def test_ArrivageUpdateForm_new_land(self):
        """New fields 'nouveau_pays'et 'nouveau_lieu' permettent de rajouter
          ces instances de coordinates.Pays et coordinates.Localite"""
        data = {'date': date(2017, 3, 1),
                'designation': 'Arrivage-1',
                'devise': self.chf.id,
                'nouveau_pays' : 'France',
                'code_pays' : 'FR',
                'lieu_provenance': self.location_lausanne.id}
        form = ArrivageUpdateForm(data)
        self.assertTrue(form.is_valid(), form.errors.as_data())
        self.assertEqual(Pays.objects.filter(nom='France').count(), 1, "France not created.")
        france = Pays.objects.filter(nom='France').first()
        self.assertEqual('FR', france.code)

    def test_ArrivageUpdateForm_new_frais(self):
        data = {'date': date(2017, 3, 1),
                'designation': 'Arrivage-1',
                'devise': self.chf.id,
                'pays' : self.ch.id,
                'lieu_provenance': self.location_lausanne.id,
                'frais_montant' : 20.00,
                'frais_objet' : 'Train Lausanne-Sion',
                'frais_devise' : self.chf.id,
                }
        form = ArrivageUpdateForm(data)
        form.instance = self.arrivage
        self.assertTrue(form.is_valid(), form.errors.as_data())


