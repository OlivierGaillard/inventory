from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Permission, User
from django.test import TestCase
from django.http import HttpRequest
from django.shortcuts import reverse
from django.test import TestCase, Client
from datetime import date
from decimal import Decimal
from money import Money
from finance.models import Currency, FraisArrivage, FraisType
from accessories.models import Accessory, AccessoryMarque, AccessoryCategory, AccessoryEntry, AccessoryOutput, InventoryAccessory
from coordinates.models import Arrivage, Pays, Localite
from coordinates.forms import ArrivageCreateForm, ArrivageUpdateForm
from products.models import Enterprise



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


        self.ch = Pays.objects.create(nom='Suisse', code='CH')
        self.chf = Currency.objects.create(currency_code='CHF', currency_name = 'Swiss Franc',
                                           used=True, rate_usd=0.9981)
        self.arrivage.devise = self.chf
        self.arrivage.save()

        self.xof = Currency.objects.create(currency_code='XOF', rate_usd=600.5791)
        self.hublot = AccessoryMarque.objects.create(nom_marque = 'Hublot')
        self.constant = AccessoryMarque.objects.create(nom_marque = 'Constant')

        self.frais_type_transport = FraisType.objects.create(nom='transport')
        self.frais_type_repas = FraisType.objects.create(nom='repas')

        self.location_lausanne = Localite.objects.create(nom='Lausanne')

        self.enterprise_hublot = Enterprise(name='Hublot')

        content_type = ContentType.objects.get_for_model(Accessory)
        permission = Permission.objects.get(
            codename='view_achat',
            content_type=content_type,
        )

        self.passwd = 'titi_grognon234'
        self.user_boss = 'Boss'
        self.boss = User.objects.create_user(username=self.user_boss, password=self.passwd)
        self.boss.user_permissions.set([permission])

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

    def btest_view_add_frais_to_arrivage(self):
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
        frais_count = FraisArrivage.objects.filter(arrivage_ref=self.arrivage).count()
        self.assertEqual(2, frais_count)

        # To add Frais to one arrivage
        c = Client()
        c.login(username=self.user_boss, password=self.passwd)

        frais_arrivage3 = FraisArrivage()
        frais_arrivage3.devise_id = self.chf
        frais_arrivage3.montant = 15.00
        frais_arrivage3.objet = 'repas'
        frais_arrivage3.frais_type = self.frais_type_repas
        frais_arrivage3.save()
        self.arrivage.fraisarrivage_set.add(frais_arrivage3)
        frais_count = self.arrivage.fraisarrivage_set.count()
        self.assertEqual(3, frais_count)

        cat = AccessoryCategory(parent=self.cat2, title='boum')
        cat.save()
        data = {'type_client': 'F',
                'categories': (cat.id,),
                'name': 'Maman', 'marque': 'Baba au rhum',
                'quantity': '5',
                'arrivage': self.arrivage.id,
                }

        form = AccessoryForm(data)
        self.assertTrue(form.is_valid(), form.errors.as_data())
        #         form.save()

        response = c.post(reverse('accessories:create'), data,
                          follow=True)
        print(response.status_code)
        c = Client()
        self.assertTrue(2 == 4, "TODo")

    def test_arrivage_get_total(self):
        '''One arrivage model has its own method get_total().
        Return the total in the main currency of the arrivage.'''
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
        frais_arrivage3 = FraisArrivage()
        frais_arrivage3.devise_id = self.chf
        frais_arrivage3.montant = 15.00
        frais_arrivage3.objet = 'repas'
        frais_arrivage3.frais_type = self.frais_type_repas
        frais_arrivage3.save()
        self.arrivage.fraisarrivage_set.add(frais_arrivage3)
        self.assertAlmostEqual(Decimal(1335.00), self.arrivage.get_total_frais().amount, 1)

    def test_arrivage_get_total_frais_multicurrency(self):
        '''One arrivage model has its own method get_total().
        Return the total in the main currency of the arrivage.'''
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
        frais_arrivage3 = FraisArrivage()
        frais_arrivage3.devise_id = self.xof
        frais_arrivage3.montant = 15.00
        frais_arrivage3.objet = 'repas'
        frais_arrivage3.frais_type = self.frais_type_repas
        frais_arrivage3.save()
        self.arrivage.fraisarrivage_set.add(frais_arrivage3)
        self.arrivage.save()
        self.assertAlmostEqual(Decimal(1320.02), self.arrivage.get_total_frais().amount, 1)


    def test_ArrivageCreateForm(self):
        """New fields 'nouveau_pays'et 'nouveau_lieu' permettent de rajouter
          ces instances de coordinates.Pays et coordinates.Localite
          """
        data = {'date' : date(2017, 3, 1),
                'designation' :'Arrivage-1',
                'devise' : self.chf.id,
                'enterprise' : '1'}
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
                'enterprise' : self.enterprise_hublot,
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


