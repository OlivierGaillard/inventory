from django.http import HttpRequest
from django.test import TestCase, Client
from django.shortcuts import reverse
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Permission, User
from django.core.management import call_command
from django.utils.six import StringIO
from money import Money, xrates
from finance.models import Converter
import pickle
import os
from decimal import Decimal
from faker import Factory, Faker
from faker.providers import BaseProvider
import random
from money import Money
from .models import Currency, Vente
from accessories.models import Accessory, AccessoryCategory, AccessoryEntry, AccessoryOutput
from clothes.models import ClothesCategory, Clothes, ClothesEntry
from shoes.models import Shoe, ShoeCategory, ShoeEntry
from coordinates.models import Contact
from finance.models import Vente, ProductType
from finance.forms import VenteCreateForm
from finance.views import make_selling
from products.models import Enterprise



class AccessoryCategoryProvider(BaseProvider):
    def category(self):
        ids_L = [a.id for a in AccessoryCategory.objects.all()]
        return AccessoryCategory.objects.get(id=random.choice(ids_L))

class ClothesCategoryProvider(BaseProvider):
    def category(self):
        ids_L = [a.id for a in ClothesCategory.objects.all() ]
        return ClothesCategory.objects.get(id=random.choice(ids_L))

class ShoeCategoryProvider(BaseProvider):
    def category(self):
        ids_L = [a.id for a in ShoeCategory.objects.all() ]
        return ShoeCategory.objects.get(id=random.choice(ids_L))

class TestFinance(TestCase):

    fixtures = ['accessoryCategories.json', 'clothescat.json', 'shoescat.json', 'productTypes.json']
    
    def setUp(self):        
        self.converter = Converter()
        # Creating a fake client
        fake = Factory.create('fr_FR')
        self.client = Contact.objects.create(prenom=fake.first_name(), nom=fake.last_name(), email=fake.email())
        enterprise = Enterprise.objects.create(name=fake.company())
        self.a1 = Accessory.objects.create(name=fake.first_name_female(), product_owner=enterprise)
        catfake = Faker()
        catfake.add_provider(AccessoryCategoryProvider)
        cat = catfake.category()
        self.a1.categories.add(cat)

        self.c1 = Clothes.objects.create(name=fake.company(), product_owner=enterprise)
        clothesfake = Faker()
        clothesfake.add_provider(ClothesCategoryProvider)
        clothcat = clothesfake.category()
        self.c1.categories.add(clothcat)

        self.s1 = Shoe.objects.create(name=fake.company(), product_owner=enterprise)
        shoesfake = Faker()
        shoesfake.add_provider(ShoeCategoryProvider)
        shoecat = shoesfake.category()
        self.s1.categories.add(shoecat)


        self.product_type_accessory = ProductType.objects.get(model_class='Accessory')
        self.product_type_clothes = ProductType.objects.get(model_class='Clothes')
        self.product_type_shoes = ProductType.objects.get(model_class='Shoe')

        content_type = ContentType.objects.get_for_model(Accessory)
        permission = Permission.objects.get(
            codename='view_achat',
            content_type=content_type,
        )

        self.passwd = 'titi_grognon234'
        self.user_boss = 'Boss'
        boss = User.objects.create_user(username=self.user_boss, password=self.passwd)
        boss.user_permissions.set([permission])



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


    def test_get_quantity_of_article_after_selling(self):
        """On crée quelques articles. On vérifie la quantité en stock. Puis on
        en vend et on valide les quantités. Il s'agit des quantités non pas
        de l'inventaire mais de la quantité actuelle fournie par la méthode
        *get_quantity* de chaque article.
        """

        # Creating a fake client and Accessory in Setup
        fake = Factory.create('fr_FR')
        entry_date = fake.past_date()
        created_quantity = random.randint(1,20)
        AccessoryEntry.objects.create(article=self.a1, date=entry_date, quantity=created_quantity)
        self.assertEqual(created_quantity, self.a1.get_quantity())
        sell_quantity = random.randint(1, 5) # Must be less than created_quantity entry
        quantity_balance = created_quantity - sell_quantity
        sell_date = fake.future_datetime()

        vente = Vente(product_id=self.a1.id, quantity=sell_quantity, client_id=self.client,
                       product_type=self.product_type_accessory, date_vente=sell_date)
        vente.save() # Accessory/Clothes/Shoe-Output is created during saving.

        # The following request allow us to retrieve all sellings
        # of the accessory 'a1'.

        selling_of_a1 =  Vente.objects.filter(product_id = self.a1.pk).count()
        self.assertEqual(1, selling_of_a1)
        accessory_total_ventes = Vente.objects.filter(product_type=self.product_type_accessory).count()
        self.assertEqual(accessory_total_ventes, selling_of_a1)
        a1_balance = self.a1.get_quantity()
        msg = "Awaited created_quantity balance was %s but we got %s." % (quantity_balance, a1_balance)
        self.assertEqual(a1_balance, quantity_balance, msg)

    def test_selling_more_than_available_quantity(self):
        """Ensure selling is not possible if available quantity is exceeded.

        We validate at the form level.
        """
        # Creating a fake client and Accessory in Setup
        fake = Factory.create('fr_FR')
        entry_date = fake.past_date()
        created_quantity = random.randint(1,5)
        AccessoryEntry.objects.create(article=self.a1, date=entry_date, quantity=created_quantity)
        sell_quantity = random.randint(6,10)
        data = {
            'quantity' : sell_quantity,
            'product_type' : self.product_type_accessory.pk,
            'product_id' : self.a1.id,
            'client_id' : self.client.id,
        }
        form = VenteCreateForm(data)
        self.assertFalse(form.is_valid(), form.errors.as_data())


    def test_selling_form_quantity(self):
        """Ensure form does not accept quantity zero.

        We validate at the form level.
        """
        # Creating a fake client and Accessory in Setup
        fake = Factory.create('fr_FR')
        entry_date = fake.past_date()
        created_quantity = random.randint(1,5)
        AccessoryEntry.objects.create(article=self.a1, date=entry_date, quantity=created_quantity)
        data = {
            'quantity' : 0,
            'product_type' : self.product_type_accessory.pk,
            'product_id' : self.a1.id,
            'client_id' : self.client.id,
        }
        form = VenteCreateForm(data)
        self.assertFalse(form.is_valid(), form.errors.as_data())


    def test_GET_selling_view(self):
        """Check the validation with the view included.

        The clean method for the quantity raised an error before
        the POST is called. Why? Because the view passed data
        during the creation of the form instance."""

        fake = Factory.create('fr_FR')
        entry_date = fake.past_date()
        created_quantity = random.randint(1, 5)
        AccessoryEntry.objects.create(article=self.a1, date=entry_date, quantity=created_quantity)
        c = Client()
        c.login(username=self.user_boss, password=self.passwd)

        response = c.get(reverse('finance:create_vente',
                                  kwargs={'product_type' : 'Accessory', 'product_id': self.a1.pk,
                                          }
                                 ), follow=False)


    def test_selling_of_multiple_article_types(self):
        """"""
        # Creating a fake client
        fake = Factory.create('fr_FR')
        sell_date = fake.future_datetime()

        accessory_entries = random.randint(1 ,25)
        clothes_entries = random.randint(1, 25)
        # Making entry of Accessory (see Setup)
        fake = Factory.create('fr_FR')
        entry_date = fake.past_date()
        AccessoryEntry.objects.create(article=self.a1, date=entry_date, quantity=accessory_entries)

        # Making entry of Clothes

        ClothesEntry.objects.create(article=self.c1, date=entry_date, quantity=clothes_entries)

        # Randomly defining selling quantity.
        sell_accessory_quantity = random.randint(1, accessory_entries)
        quantity_balance_accessory = accessory_entries - sell_accessory_quantity

        sell_cloth_quantity = random.randint(1, clothes_entries)
        quantity_balance_clothes = clothes_entries - sell_cloth_quantity

        sell_date = fake.future_datetime()

        # Selling accessories and clothes
        vente = Vente(product_id=self.a1.id, quantity=sell_accessory_quantity, client_id=self.client,
                      product_type=self.product_type_accessory, date_vente=sell_date)
        vente.save()  # Accessory/Clothes/Shoe-Output is created during saving.
        self.assertEqual(vente.product_owner, self.a1.product_owner)


        vente = Vente(product_id=self.c1.id, quantity=sell_cloth_quantity, client_id=self.client,
                      product_type=self.product_type_clothes, date_vente=sell_date)
        vente.save()  # Accessory/Clothes/Shoe-Output is created during saving.

        # Validation of Accessory
        selling_of_a1 = Vente.objects.filter(product_id=self.a1.pk).filter(product_type=self.product_type_accessory).count()
        self.assertEqual(1, selling_of_a1)
        accessory_total_ventes = Vente.objects.filter(product_type=self.product_type_accessory).count()
        self.assertEqual(accessory_total_ventes, selling_of_a1)
        a1_balance = self.a1.get_quantity()
        msg = "Awaited quantity balance was %s but we got %s." % (quantity_balance_accessory, a1_balance)
        self.assertEqual(a1_balance, quantity_balance_accessory, msg)


        # Validation of Clothes
        selling_of_c1 = Vente.objects.filter(product_id=self.c1.pk).filter(product_type=self.product_type_clothes).count()
        self.assertEqual(1, selling_of_c1)
        clothes_total_ventes = Vente.objects.filter(product_type=self.product_type_clothes).count()
        self.assertEqual(clothes_total_ventes, selling_of_c1)
        c1_balance = self.c1.get_quantity()
        self.assertEqual(c1_balance, quantity_balance_clothes)



    def test_selling_to_client(self):

        # Preparing entries
        accessory_entries = random.randint(1, 25)
        clothes_entries = random.randint(1, 25)
        shoes_entries = random.randint(1, 25)
        # Making entry of Accessory
        fake = Factory.create('fr_FR')
        entry_date = fake.past_date()

        AccessoryEntry.objects.create(article=self.a1, date=entry_date, quantity=accessory_entries)
        ClothesEntry.objects.create(article=self.c1, date=entry_date, quantity=clothes_entries)
        ShoeEntry.objects.create(article=self.s1, date=entry_date, quantity=shoes_entries)

        sell_accessory_quantity = random.randint(1, accessory_entries)
        quantity_balance_accessory = accessory_entries - sell_accessory_quantity

        sell_cloth_quantity = random.randint(1, clothes_entries)
        quantity_balance_clothes = clothes_entries - sell_cloth_quantity

        sell_shoes_quantity = random.randint(1, shoes_entries)
        quantity_balance_shoes = shoes_entries - sell_shoes_quantity

        sell_date = fake.future_date()
        vente = Vente(product_id=self.a1.id, quantity=sell_accessory_quantity, client_id=self.client,
                      product_type=self.product_type_accessory, date_vente=sell_date)
        vente.save()
        vente = Vente(product_id=self.c1.id, quantity=sell_cloth_quantity, client_id=self.client,
                      product_type=self.product_type_clothes, date_vente=sell_date)
        vente.save()

        vente = Vente(product_id=self.s1.id, quantity=sell_shoes_quantity, client_id=self.client,
                      product_type=self.product_type_shoes, date_vente=sell_date)
        vente.save()

        # Retrieving client's selling
        accessory_ventes = Vente.objects.filter(product_type=self.product_type_accessory)
        clothes_ventes   = Vente.objects.filter(product_type=self.product_type_clothes)
        shoes_ventes = Vente.objects.filter(product_type=self.product_type_shoes)
        self.assertEqual(3, accessory_ventes.count() + clothes_ventes.count() + shoes_ventes.count())

        client_ventes = Vente.objects.filter(client_id=self.client)
        self.assertEqual(3, client_ventes.count())
        
        
        
        
