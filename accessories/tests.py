import pdb
from django.contrib.auth.models import Permission, User, Group
from django.contrib.auth.decorators import user_passes_test
from django.contrib.contenttypes.models import ContentType
#from django.shortcuts import reverse
from django.urls import reverse
from django.test import TestCase, Client, RequestFactory

from datetime import date
from faker import Factory, Faker
from faker.providers import BaseProvider
import random
from finance.models import Currency
from products.models import Enterprise, Employee
from .models import Accessory, AccessoryMarque, AccessoryCategory, AccessoryEntry, AccessoryOutput, InventoryAccessory
from .forms import AccessoryForm, AccessoryCategoryForm, AccessoryUpdateForm
from .views import AccessoryCreationView, AccessoryUpdateView, AccessoryListView
from finance.models import Vente, Achat
from coordinates.models import Arrivage


class CategoryProvider(BaseProvider):
    def category(self):
        ids_L = [a.id for a in AccessoryCategory.objects.all()]
        return AccessoryCategory.objects.get(id=random.choice(ids_L))


# Create your tests here.
class TestAccessoryInventory(TestCase):

    fixtures = ['accessoryCategories.json']

    def user_is_employee_of_enterprise(self, user, enterprise):
        """Once the user has made her login we can filter the views.

        As a consequence do we actually need to check if the user is
        one employee? Not so sure.
        """

        employee = Employee.objects.get(user=user)
        return employee.enterprise == enterprise

    def setUp(self):

        self.start_date = date(year=2017, month=1, day=1)
        cat1 = AccessoryCategory.objects.create(parent=None, title='Valises et sacoches')
        self.cat2 = AccessoryCategory.objects.create(parent=cat1, title='Valises')
        cat3 = AccessoryCategory.objects.create(parent=cat1, title='Sacoches')
        self.enterprise_arvo = Enterprise.objects.create(name='Tabula Rasa')

        # These ones are used to test create and update forms and views.
        self.cat = AccessoryCategory(parent=self.cat2, title='boum')
        self.cat.save()


        self.chf = Currency.objects.create(currency_code='CHF', rate_usd=0.9981, used=True)
        self.hublot = AccessoryMarque.objects.create(nom_marque = 'Hublot')
        self.constant = AccessoryMarque.objects.create(nom_marque = 'Constant')

        content_type = ContentType.objects.get_for_model(Accessory)
        permission = Permission.objects.get(
            codename='view_achat',
            content_type=content_type,
        )



        self.passwd = 'titi_grognon234'
        user_boss = 'Boss'
        self.boss = User.objects.create_user(username=user_boss, password=self.passwd)
        self.boss.user_permissions.set([permission])
        self.enterprise_grognon = Enterprise(name='grognon')
        self.enterprise_grognon.save()
        Employee.objects.create(user=self.boss, enterprise=self.enterprise_grognon)
        self.arrivage_boss = Arrivage(date=date(2017, 2, 1), designation='Arrivage-1',
                                      enterprise=self.enterprise_grognon)
        self.arrivage_boss.save()


        self.arvoe_passwd = 'part'
        self.arvoe = User.objects.create_user(username='arvoe', password=self.arvoe_passwd)
        self.arvoe.user_permissions.set([permission])
        Employee.objects.create(user=self.arvoe, enterprise=self.enterprise_arvo)

        self.arrivage_arvo = Arrivage(date=date(2017, 5, 1), designation='Arrivage-Part',
                                      enterprise=self.enterprise_arvo)
        self.arrivage_arvo.save()

    def do_E(self, date_entree, a, qte):
        """ Create one Entry  with the given quantity 'qte'.
        """
        a = self.accessories_li[a]
        AccessoryEntry.objects.create(article=a, date=date_entree, quantity=qte)

    def do_S(self, date, a, qte):
        """ Update as many 'Exemplaire' instances' date_sortie as 'qte'.
        """
        a = self.accessories_li[a]
        date_sortie = date
        AccessoryOutput.objects.create(date=date, article=a, quantity=qte)

    def get_art(self, art_code):
        return self.accessories_li[art_code]

    def btest_faker(self):
        """Make instances of Accessory using faker."""
        fake = Factory.create('fr_FR')
        arrivage = Arrivage(date=date(2017, 3, 1), designation=fake.region())
        arrivage.save()
        mnt = random.randint(20,200)
        qte = random.randint(1,10)
        achat = Achat(montant=mnt, quantite=qte, date_achat=fake.date_time_this_month().date(),
                      devise_id=self.chf)
        achat.save()
        a = Accessory(name=fake.company(), type_client='F', arrivage=arrivage,
                    prix_achat=achat)
        a.save()
        catfake = Faker()
        catfake.add_provider(CategoryProvider)
        cat = catfake.category()
        a.categories.add(cat)
        self.assertEqual(3, Accessory.objects.count())



    def test_case0(self):
        """Tester les dates d'entrée et de sortie d'un exemplaire.
        Ce test suggère cette procédure:
        1. on crée un article.
        2. on crée une entrée
        3. on génère un inventaire pour obtenir une mise à jour des quantités.
        Il est requis de pouvoir interroger sur l'état des stocks sans passer
        par la création d'un inventaire. On peut le faire simplement avec une
        méthode définie sur le type entité 'Article': get_quantity()
        """

        a1 = Accessory.objects.create(name='Valise-1', product_owner=self.enterprise_arvo)
        a1.categories.add(self.cat2)
        a2 = Accessory.objects.create(name='Sacoche-1', product_owner=self.enterprise_arvo)
        a2.categories.add(self.cat2)

        self.accessories_li = {'a1': a1, 'a2': a2}
        for k in self.accessories_li.keys():
            a = self.accessories_li[k]
            a.save()


        d1 = date(2017, 1, 1)
        d2 = date(2017, 1, 10)
        creation_date = date(2017, 2, 1)  # Inventory creation date
        self.do_E(d1, 'a1', 4)
        a1 = self.get_art('a1')  # getting the 'Article' instance with key 'a1'.
        inventory = InventoryAccessory()
        inventory.set_enterprise_of_current_user(self.enterprise_arvo)
        a1_count = inventory.get_quantity(a1, self.start_date, end_date=d2)
        # The inventory is not yet created then no entry in
        # inventory exist.
        self.assertEqual(0, a1_count)
        # But we created one Entree, then the quantity of a1 should be 4.
        self.assertEqual(4, a1.get_quantity())
        # An inventory is generated, using the current date
        inventory.sum_entries(creation_date)
        self.assertTrue(InventoryAccessory.objects.count() == 1)
        # The entry of inventory should be right.
        # But the generated entry of the inventory is current date.
        # As a result the get_quantity must use the current date to find
        # result.
        a1_count = inventory.get_quantity(a1, self.start_date, end_date=date.today())
        self.assertEqual(4, a1_count)
        # If we try to get the inventory of last year, which does not exist,
        # we should get zero.
        a1_qte_lastyear = inventory.get_quantity(a1,
                                                  date(year=2016, month=1, day=1),
                                                  date(year=2016, month=12, day=31))
        self.assertEqual(0, a1_qte_lastyear)
        # The same holds for dates after the inventory creation date: 1st feb 2017
        start_date = date(year=2017, month=2, day=2)  # 2nd february 2017
        end_date = date(year=2017, month=3, day=31)
        a1_count_future = inventory.get_quantity(a1, start_date, end_date)
        self.assertEqual(0, a1_count_future)
        #
        self.do_S(d2, 'a1', 2)
        self.assertEqual(2, a1.get_quantity())
        # # But in inventory the quantity is still 4.
        self.assertEqual(4, inventory.get_quantity(a1, self.start_date, date.today()))
        inventory.sum_entries(creation_date=date(2017, 3, 1))  # generate inventory
        # # After update of inventory:
        self.assertEqual(2, inventory.get_quantity(a1, self.start_date, date.today()))
        self.do_S(d2, 'a1', 2)
        self.assertEqual(0, a1.get_quantity())
        # # But the quantity of Inventory is still the old one:
        self.assertEqual(2, inventory.get_quantity(a1, self.start_date, date.today()))


    def test2_form(self):
        cat = AccessoryCategory(parent=self.cat2, title='boum')
        cat.save()
        data = {'type_client': 'F',
                'categories': (cat.id,),
                'name': 'Maman', 'marque': 'Babar',
                'quantity': '5',
                'arrivage': self.arrivage_boss.id,
                'product_owner': self.enterprise_grognon.id,
                }
        form = AccessoryForm(data)
        self.assertTrue(form.is_valid())


    def test_generate_inventory(self):
        """
        The inventory will be generated for the articles of the enterprise to which the employee
        belongs to.
        :return: The result of sum (entries) substracted from sum (outputs)
        """
        c = Client()
        c.login(username=self.boss, password=self.passwd)

        # Creating 2 accessories and adding the category cat2
        a1 = Accessory.objects.create(name='Valise-1', product_owner=self.enterprise_grognon)
        a1.categories.add(self.cat2)
        sacoche = Accessory.objects.create(name='Sacoche-1', product_owner=self.enterprise_grognon)
        sacoche.categories.add(self.cat2)

        # Creating 2 entries (the view AccessoryCreationView does it during the 'form_valid' call.
        AccessoryEntry.objects.create(article=a1, date=date(2017, 1, 1), quantity=2)
        AccessoryEntry.objects.create(article=sacoche, date=date(2017, 1, 1), quantity=4)

        # We add one Accessory belonging to **another** enterprise.
        sac_a_main = Accessory.objects.create(name='Sac à main', product_owner=self.enterprise_arvo)
        AccessoryEntry.objects.create(article=sac_a_main, date=date(2017, 1, 3), quantity=5)

        # Simulating 1 selling
        AccessoryOutput.objects.create(article=sacoche, date=date(2017, 1, 2), quantity=1)

        # Generating the inventory with the view only for the enterprise of the user
        creation_date = date(2017, 2, 1)
        data = {'creation_date': creation_date}
        c.post(reverse('accessories:inventory-create'),
                          data, follow=False)

        count = InventoryAccessory.objects.count()
        self.assertTrue(count == 2, "Not 2 inventory entries but %s" % count)

        # Checking the quantity of sacoche
        inventory_sacoche = InventoryAccessory.objects.filter(article=sacoche)
        quantity_sacoche = inventory_sacoche[0].quantity
        self.assertEqual(3, quantity_sacoche, ("Not 3 sacoches but %s", str(quantity_sacoche)))

    def test_generate_inventory_2(self):
        """
        Two inventoriew will be generated, one per logged user.
        :return: The result of sum (entries) substracted from sum (outputs)
        """
        c = Client()
        c.login(username=self.boss, password=self.passwd)

        # Creating 2 accessories and adding the category cat2
        a1 = Accessory.objects.create(name='Valise-1', product_owner=self.enterprise_grognon)
        a1.categories.add(self.cat2)
        sacoche = Accessory.objects.create(name='Sacoche-1', product_owner=self.enterprise_grognon)
        sacoche.categories.add(self.cat2)

        # Creating 2 entries (the view AccessoryCreationView does it during the 'form_valid' call.
        AccessoryEntry.objects.create(article=a1, date=date(2017, 1, 1), quantity=2)
        AccessoryEntry.objects.create(article=sacoche, date=date(2017, 1, 1), quantity=4)

        # We add one Accessory belonging to **another** enterprise.
        sac_a_main = Accessory.objects.create(name='Sac à main', product_owner=self.enterprise_arvo)
        AccessoryEntry.objects.create(article=sac_a_main, date=date(2017, 1, 3), quantity=5)

        # Simulating 1 selling
        AccessoryOutput.objects.create(article=sacoche, date=date(2017, 1, 2), quantity=1)

        # Generating the inventory with the view only for the enterprise of the user
        creation_date = date(2017, 2, 1)
        data = {'creation_date': creation_date}
        c.post(reverse('accessories:inventory-create'),
                          data, follow=False)

        c.logout()

        c2 = Client()
        c2.login(username=self.arvoe, password=self.arvoe_passwd)
        creation_date = date(2017, 2, 10)
        data = {'creation_date': creation_date}
        c2.post(reverse('accessories:inventory-create'),
               data, follow=False)

        response = c2.get(reverse('accessories:inventory-list'))
        self.assertNotIn('Sacoche', response.content.decode(), "Found article 'Sacoche' of another enterprise than arvoe's Tabula Rasa.")



    def test_create_form(self):
        data = {'type_client': 'F',
                'categories': (self.cat.id,),
                'name': 'Maman', 'marque': 'Babar',
                'quantity': '10', 'product_owner': self.enterprise_arvo.id,
                'arrivage': self.arrivage_arvo.id}

        form = AccessoryForm(data)
        self.assertTrue(form.is_valid())


    def test_create_marque_empty(self):
        data = {'type_client': 'F',
                'categories': (self.cat.id,),
                'name': 'Maman', 'marque': '',
                'quantity': '10',
                'arrivage': self.arrivage_boss.id}
        form = AccessoryForm(data)
        self.assertFalse(form.is_valid())

    def test_select_marque_ref(self):
        data = {'type_client': 'F',
                'categories': (self.cat.id,),
                'name': 'Maman', 'marque': '',
                'marque_ref': self.hublot.id,
                'quantity': '10', 'product_owner': self.enterprise_arvo.id,
                'arrivage': self.arrivage_arvo.id}
        form = AccessoryForm(data)
        #print(form.errors.as_data())
        self.assertTrue(form.is_valid())

    def test_forms_to_add_new_marque_for_new_accessory(self):
        data = {'type_client': 'F',
                'categories': (self.cat.id,),
                'name': 'Maman', 'marque': 'Babar',
                'quantity': '10',
                'arrivage': self.arrivage_arvo.id,
                'product_owner': self.enterprise_arvo.id}
        form = AccessoryForm(data)
        self.assertTrue(form.is_valid(), form.errors.as_data())
        data = {'type_client': 'F',
                'categories': (self.cat.id,),
                'name': 'Maman', 'marque': 'Babar',
                'quantity': '10',
                'arrivage': self.arrivage_arvo.id}
        data['montant'] = 20.00
        data['quantite_achetee'] = 5
        data['date_achat'] = date(2017, 1, 20)
        data['devise'] = self.chf.id
        data['quantite_type'] = 1
        form = AccessoryUpdateForm(data)
        self.assertTrue(form.is_valid(), form.errors.as_data())

    def prepare_update_data(self):
        data = self.prepare_initial_data()
        data['montant'] = 20.00
        data['quantite_achetee'] = 5
        data['date_achat'] = date(2017, 1, 20)
        chf_id = Currency.objects.get(currency_code='CHF').id
        data['devise'] = chf_id
        data['quantite_type'] = 1  # à l'unité
        data['marque_ref'] = None
        return data

    def test_view_create_accessory(self):
        c = Client()
        c.login(username=self.arvoe, password=self.arvoe_passwd)

        # Create one accessory entry with the help of the view to enter a quantity
        # because only using the model is impossible, as it has not this field 'quantity'.
        cat = AccessoryCategory(parent=self.cat2, title='boum')
        cat.save()
        data = {'type_client': 'F',
                'categories': (cat.id,),
                'name': 'Maman', 'marque': 'Baba au rhum',
                'quantity': '5', 'product_owner': self.enterprise_arvo.id,
                'arrivage': self.arrivage_arvo.id,
                }

        form = AccessoryForm(data)
        self.assertTrue(form.is_valid(), form.errors.as_data())

        response = c.post(reverse('accessories:create'), data,
                          follow=True)
        # Check if entries were created.
        # There is only one because in the tests' Setup we only create Accessory
        # instances of model 'Accessory' without quantity.
        self.assertEqual(1, len(AccessoryEntry.objects.all()))
        self.assertIn('Mama', response.content.decode())

        # Check if the Input's date is equal to the Arrivage's one
        accessoryEntry = AccessoryEntry.objects.last()
        self.assertEqual(self.arrivage_arvo.date, accessoryEntry.date)
        # Check quantity of Entry created
        self.assertEqual(5, accessoryEntry.quantity)
        accessory = Accessory.objects.all().last()
        self.assertEqual(5, accessory.get_quantity(), 'get_quantity of Accessory is invalid.')

    def test_update_quantity(self):
        c = Client()
        self.assertTrue(c.login(username=self.boss.username, password=self.passwd))
        data = {'type_client': 'F',
                'categories': (self.cat.id,),
                'name': 'Maman234', 'marque': 'Babar',
                'quantity': '10', 'product_owner': self.enterprise_grognon.id,
                'arrivage': self.arrivage_boss.id}
        response = c.post(reverse('accessories:create'),
                          data, follow=True)

        # Check if one entry was crated.
        self.assertEqual(1, len(Accessory.objects.all()))
        self.assertEqual(1, len(AccessoryEntry.objects.all()))
        self.assertIn('Mama', response.content.decode())

        # Check if the Input's date is equal to the Arrivage's one
        accessoryEntry = AccessoryEntry.objects.last()
        self.assertEqual(date(2017, 2, 1), accessoryEntry.date)
        self.assertEqual(10, accessoryEntry.quantity)
        accessory = Accessory.objects.all().last()

        self.assertEqual(10, accessory.get_quantity())
        c.logout()

        # Now we set a new marque
        c2 = Client()
        c2.login(username=self.boss.username, password=self.passwd)
        data['montant'] = 20.00
        data['quantite_achetee'] = 5
        data['date_achat'] = date(2017, 1, 20)
        chf_id = Currency.objects.get(currency_code='CHF').id
        data['devise'] = chf_id
        data['quantite_type'] = 1  # à l'unité
        data['marque'] = 'Baobab'
        data['quantity'] = '8'
        data['quantite_achetee'] = '15'
        self.assertEqual('8', data['quantity'])
        updateform = AccessoryUpdateForm(data)
        self.assertTrue(updateform.is_valid(), updateform.errors.as_data())
        response = c2.post(reverse('accessories:update', kwargs={'pk': accessory.pk}),
                           data=data, follow=True)
        self.assertNotEqual(404, response.status_code, "Submit failed!")
        # Checking new quantity
        accessoryEntry = AccessoryEntry.objects.last()
        accessory = Accessory.objects.all().last()

        self.assertEqual(accessoryEntry.article.pk, accessory.pk)
        self.assertEqual(8, accessoryEntry.quantity)
        self.assertEqual(8, accessory.get_quantity())
        self.assertEqual(15, accessory.prix_achat.quantite)

    def test_check_new_marque_is_saved(self):
        c = Client()
        c.login(username=self.boss.username, password=self.passwd)
        data = {'type_client': 'F',
                'categories': (self.cat.id,),
                'name': 'Maman', 'marque_ref': self.hublot.id,
                'quantity': '10', 'product_owner': self.enterprise_grognon.id,
                'arrivage': self.arrivage_boss.id}

        response = c.post(reverse('accessories:create'),
                                        data, follow=True)
        self.assertEqual(200, response.status_code)
        # Check if entries were created.
        # There is only one because in the tests' Setup we only create Accessory
        # instances of model 'Accessory' without quantity.
        accessoryEntry = AccessoryEntry.objects.last()
        accessory = Accessory.objects.all().last()
        self.assertEqual(10, accessory.get_quantity())

        # Now we set a new marque
        c2 = Client()
        c2.login(username=self.boss.username, password=self.passwd)
        data['montant'] = 20.00
        data['quantite_achetee'] = 5
        data['date_achat'] = date(2017, 1, 20)
        data['devise'] = self.chf.id
        data['quantite_type'] = 1  # à l'unité
        data['marque_ref'] = self.constant.id
        data['quantity'] = '8'
        data['quantite_achetee'] = '15'
        self.assertEqual('8', data['quantity'])
        updateform = AccessoryUpdateForm(data)
        self.assertTrue(updateform.is_valid(), updateform.errors.as_data())
        response = c2.post(reverse('accessories:update', kwargs={'pk': accessory.pk}),
                           data=data, follow=True)
        self.assertNotEqual(404, response.status_code, "Submit failed!")
        # Checking new quantity
        accessoryEntry = AccessoryEntry.objects.last()
        accessory = Accessory.objects.all().last()
        self.assertEqual(8, accessory.get_quantity())
        self.assertEqual(8, accessoryEntry.quantity)
        # Chechking new marque is set
        self.assertEqual(accessory.marque_ref, self.constant)


    def test_categoryform(self):
        data = {'parent':'',
                'title': 'Valise'}
        form = AccessoryCategoryForm(data)
        self.assertTrue(form.is_valid())

    def test_permission1(self):
        content_type = ContentType.objects.get_for_model(Accessory)
        permission = Permission.objects.create(
            codename='view_achat_test',
            name='Can View Achat',
            content_type=content_type,
        )


        permission   = Permission.objects.get(
            codename = 'view_achat_test',
            content_type = content_type,
        )
        group_manager = Group.objects.create(name='manager')
        group_manager.permissions.add(permission)
        toto = User.objects.create(username='Toto')
        alpha = User.objects.create(username='AlphaSud')
        alpha.groups.add(group_manager)
        self.assertFalse(group_manager in toto.groups.all())
        self.assertTrue(group_manager  in alpha.groups.all())

    def test_permission2(self):
        """I retain this solution because it is very easy to test in templates."""
        content_type = ContentType.objects.get_for_model(Accessory)
        permission = Permission.objects.get(
            codename='view_achat',
            content_type=content_type,
        )

        alpha = User.objects.create(username='alpha')
        alpha.user_permissions.set([permission])
        self.assertTrue(alpha.has_perm('accessories.view_achat'))

    def test_employee_partnership_to_enterprise(self):
        """Test that employee may access only the data of her enterprise."""

        arvo  = Enterprise.objects.create(name='Tabula Rasa')
        alpha = User.objects.create(username='alpha')
        employee_alpha = Employee.objects.create(user=alpha, enterprise=arvo)
        self.assertTrue(self.user_is_employee_of_enterprise(user=alpha, enterprise=arvo))


    def test_employee_cannot_access_other_enterprise(self):
        """Setup set accessories to the enterprise 'Tabula Rasa.

        As the user 'boss' is employee of the enterprise 'grognon'
        and because this enterprise has no articles in the inventory,
        the user receives an empty list. It should be cool to inform
        the user that his/her enterprise has no data.
        """
        c = Client()
        c.login(username=self.boss, password=self.passwd)
        response = c.get(reverse('accessories:list'))
        self.assertEqual(response.status_code, 200)

    def test_employee_can_access_its_enterprise(self):
        c = Client()
        passwd = 'titi_grognon234'
        user1 = User.objects.create_user(username='Titi', password=passwd)
        employee = Employee.objects.create(user=user1, enterprise=self.enterprise_arvo)
        c.login(username=user1, password=passwd)
        response = c.get(reverse('accessories:list'))
        self.assertEqual(response.status_code, 200, "Titi can access tabula rasa data")
        c.logout()
        user2 = User.objects.create_user(username='Toto', password=passwd)
        entreprise2 = Enterprise.objects.create(name='Mikafashion')
        # entreprise2 has no content but entreprise_arvo do have.
        employee2 = Employee.objects.create(user=user2, enterprise=entreprise2)
        c.login(username=user2, password=passwd)
        response = c.get(reverse('accessories:list'))
        self.assertIn('vide', response.content.decode(), "Not find 'vide'.")


    def btest_inventory_per_enterprise(self):
        """Test inventory generated per enterprise.

        The inventory should contain only articles belonging to the
        enterprise. This is filtered by the field 'product_owner'.
        """
        fake = Factory.create('fr_FR')

        arrivage = Arrivage(date=date(2017, 3, 1), designation=fake.region())
        arrivage.save()
        mnt = random.randint(20,200)
        qte = random.randint(1,10)
        achat = Achat(montant=mnt, quantite=qte, date_achat=fake.date_time_this_month().date(),
                      devise_id=self.chf)
        achat.save()
        a = Accessory(name=fake.company(), type_client='F', arrivage=arrivage,
                    prix_achat=achat)
        a.save()
        catfake = Faker()
        catfake.add_provider(CategoryProvider)
        cat = catfake.category()
        a.categories.add(cat)
        self.assertEqual(3, Accessory.objects.count())
