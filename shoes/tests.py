from django.shortcuts import reverse
from datetime import date
from django.test import TestCase, Client
from coordinates.models import Arrivage
from .models import Shoe, ShoeEntry, ShoeOutput,InventoryShoe, ShoeCategory
from .forms import ShoeForm, InventoryShoeForm

# Create your tests here
#
#
class TestShoeInventory(TestCase):

    def setUp(self):
        cat1 = ShoeCategory(title='Pointues')
        cat1.save()
        self.cat = ShoeCategory(parent=cat1, title='Grandes')
        self.cat.save()
        self.arrivage = Arrivage(date=date(2017, 2, 1), designation='Filles du quartier')
        self.arrivage.save()

        self.start_date = date(year=2017, month=1, day=1)
        self.cat2 = ShoeCategory.objects.create(parent=cat1, title='Sombrero moyen')
        cat3 = ShoeCategory.objects.create(parent=cat1, title='Petit sombrero')
        a1 = Shoe.objects.create(name='Chapeau rigolo')
        a1.categories.add(self.cat2)
        a2 = Shoe.objects.create(name='Chapeau dramatique')
        a2.categories.add(self.cat2)

        self.articles_li = {'a1': a1, 'a2': a2}
        for k in self.articles_li.keys():
            a = self.articles_li[k]
            a.save()

    def do_E(self, date_entree, a, qte):
        """ Create one Entry  with the given quantity 'qte'.
        """
        a = self.articles_li[a]
        ShoeEntry.objects.create(article=a, date=date_entree, quantity=qte)


    def do_S(self, date, a, qte):
        """ Update as many 'Exemplaire' instances' date_sortie as 'qte'.
        """
        a = self.articles_li[a]
        date_sortie = date
        ShoeOutput.objects.create(date=date, article=a, quantity=qte)


    def get_art(self, art_code):
        return self.articles_li[art_code]


    def test_shoe_create_form(self):
        data = {'type_client': 'F',
                'categories': (self.cat.id,),
                'name': 'Maman', 'marque': 'Babar',
                'quantity': '10',
                'arrivage': self.arrivage.id}
        form = ShoeForm(data)
        self.assertTrue(form.is_valid())

    def test_shoe_create_view(self):
        data = {'type_client': 'F',
                'categories': (self.cat.id,),
                'name': 'Maman', 'marque': 'Babar',
                'quantity': '10',
                'arrivage': self.arrivage.id}
        c = Client()
        response = c.post(reverse('shoes:shoe_create'),
                          data, follow=True)
        # Check if entries were created.
        self.assertEqual(1, len(ShoeEntry.objects.all()))


        # Check if the Input's date is equal to the Arrivage's one
        entry = ShoeEntry.objects.last()
        self.assertEqual(self.arrivage.date, entry.date)
        self.assertIn('Mama', response.content.decode())


    def test_case0(self):
        """Tester les dates d'entrée et de sortie d'un exemplaire.
        Ce test suggère cette procédure:
        1. on crée un article.
        2. on crée une entrée.
        3. on génère un inventaire pour obtenir une mise à jour des quantités.
        Il est requis de pouvoir interroger sur l'état des stocks sans passer
        par la création d'un inventaire. On peut le faire simplement avec une
        méthode définie sur le type entité 'Article': get_quantity()
        """
        d1 = date(2017, 1, 1)
        d2 = date(2017, 1, 10)
        creation_date = date(2017, 2, 1)  # Inventory creation date
        self.do_E(d1, 'a1', 4)
        a1 = self.get_art('a1')  # getting the 'Article' instance with key 'a1'.
        inventory = InventoryShoe()
        a1_count = inventory.get_quantity(a1, self.start_date, end_date=d2)
        # The inventory is not yet created then no entry in
        # inventory exist.
        self.assertEqual(0, a1_count)
        # But we created one Entree, then the quantity of a1 should be 4.
        self.assertEqual(4, a1.get_quantity())
        # An inventory is generated, using the current date
        inventory.sum_entries(creation_date)
        self.assertTrue(InventoryShoe.objects.count() == 1)
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


    def test_generate_inventory_with_view(self):
        d1 = date(2017, 1, 1)
        creation_date = date(2017, 2, 1)  # Inventory creation date
        self.do_E(d1, 'a1', 4)
        c = Client()
        data = {'creation_date' : creation_date}
        response = c.post(reverse('shoes:inventory_create'),
                          data, follow=False)

        self.assertTrue(InventoryShoe.objects.count() == 1)

