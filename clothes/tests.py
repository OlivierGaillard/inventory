from datetime import date
from django.test import TestCase, Client
from django.shortcuts import reverse
from .models import Clothes, ClothesCategory, ClothesEntry, ClothesOutput, InventoryClothes
from .forms import ClothesForm, ClothesCategoryForm, InventoryClothesForm
from coordinates.models import Arrivage


class TestClothes(TestCase):

    def setUp(self):
        cat1 = ClothesCategory(title='Sombrero')
        cat1.save()
        self.cat = ClothesCategory(parent=cat1, title='Lucy')
        self.cat.save()
        self.arrivage = Arrivage(date=date(2017, 2, 1), designation='Filles du quartier')
        self.arrivage.save()

        self.start_date = date(year=2017, month=1, day=1)
        self.cat2 = ClothesCategory.objects.create(parent=cat1, title='Sombrero moyen')
        cat3 = ClothesCategory.objects.create(parent=cat1, title='Petit sombrero')
        a1 = Clothes.objects.create(name='Chapeau rigolo')
        a1.categories.add(self.cat2)
        a2 = Clothes.objects.create(name='Chapeau dramatique')
        a2.categories.add(self.cat2)

        self.articles_li = {'a1': a1, 'a2': a2}
        for k in self.articles_li.keys():
            a = self.articles_li[k]
            a.save()


    def do_E(self, date_entree, a, qte):
        """ Create one Entry  with the given quantity 'qte'.
        """
        a = self.articles_li[a]
        ClothesEntry.objects.create(article=a, date=date_entree, quantity=qte)


    def do_S(self, date, a, qte):
        """ Update as many 'Exemplaire' instances' date_sortie as 'qte'.
        """
        a = self.articles_li[a]
        date_sortie = date
        ClothesOutput.objects.create(date=date, article=a, quantity=qte)


    def get_art(self, art_code):
        return self.articles_li[art_code]


    def test_create_form(self):

        data = {'type_client': 'F',
                'categories': (self.cat.id,),
                'name': 'Maman', 'marque': 'Babar',
                'quantity': '10',
                'arrivage': self.arrivage.id}

        form = ClothesForm(data)
        self.assertTrue(form.is_valid())


    def test_categoryform(self):
        data = {'parent': '',
                'title': 'Valise'}
        form = ClothesCategoryForm(data)
        self.assertTrue(form.is_valid())

    def test_create_view(self):
        data = {'type_client': 'F',
                'categories': (self.cat.id,),
                'name': 'Maman', 'marque': 'Babar',
                'quantity': '10',
                'arrivage': self.arrivage.id}
        c = Client()
        response = c.post(reverse('clothes:clothes_create'),
                          data, follow=True)
        # Check if entries were created.
        self.assertEqual(1, len(ClothesEntry.objects.all()))


        # Check if the Input's date is equal to the Arrivage's one
        entry = ClothesEntry.objects.last()
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
        inventory = InventoryClothes()
        a1_count = inventory.get_quantity(a1, self.start_date, end_date=d2)
        # The inventory is not yet created then no entry in
        # inventory exist.
        self.assertEqual(0, a1_count)
        # But we created one Entree, then the quantity of a1 should be 4.
        self.assertEqual(4, a1.get_quantity())
        # An inventory is generated, using the current date
        inventory.sum_entries(creation_date)
        self.assertTrue(InventoryClothes.objects.count() == 1)
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
        d2 = date(2017, 1, 10)
        creation_date = date(2017, 2, 1)  # Inventory creation date
        self.do_E(d1, 'a1', 4)

        c = Client()
        data = {'creation_date' : creation_date}
        response = c.post(reverse('clothes:inventory_create'),
                          data, follow=False)

        self.assertTrue(InventoryClothes.objects.count() == 1)

    def test_display_inventory_with_view(self):
        d1 = date(2017, 1, 1)
        d2 = date(2017, 1, 10)
        self.do_E(d1, 'a1', 4)
        inventory = InventoryClothes()
        creation_date = date(2017, 2, 1)  # Inventory creation date
        inventory.sum_entries(creation_date)

        c = Client()
        response = c.get(reverse('clothes:inventory'))
        self.assertEqual(200, response.status_code)
