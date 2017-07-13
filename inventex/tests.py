from datetime import date
from django.test import TestCase
from inventex.models import BadCreationDateException
from inventex.models import Inventory, Entree, Sortie, Article


# Create your tests here.
class TestInventex(TestCase):
    
    def setUp(self):
        self.start_date = date(year=2017, month=1, day=1)        
        ga1 = GenreArticle.objects.create(genre='a1')
        ga2 = GenreArticle.objects.create(genre='a2')
        ga3 = GenreArticle.objects.create(genre='a3')
        ga4 = GenreArticle.objects.create(genre='a4')
        ga5 = GenreArticle.objects.create(genre='a5')
        a1 = Article(genre_article=ga1)
        a2 = Article(genre_article=ga2)
        a3 = Article(genre_article=ga3)
        a4 = Article(genre_article=ga4)
        a5 = Article(genre_article=ga5)
        self.articles_li = {'a1':a1, 'a2':a2, 'a3':a3, 'a4':a4, 'a5':a5}
        for k in self.articles_li.keys():
            a = self.articles_li[k]
            a.save()
        
    def do_E(self,  date_entree, a, qte):
        """ Create as many instances of "Entree" as the quantity 'qte'.
        """
        a = self.articles_li[a]
        Entree.objects.create(article=a, date=date_entree, quantity=qte)
            
        
                
    def do_S(self, date, a, qte):
        """ Update as many 'Exemplaire' instances' date_sortie as 'qte'.
        """
        a = self.articles_li[a]
        date_sortie = date
        Sortie.objects.create(date=date, article=a, quantity=qte)

            
    def get_art(self, art_code):
        return self.articles_li[art_code]
    
    def test_case01(self):
        """Prohibit an inventory creation date older than the most recent
        entries of Entree. Inventory return silently without exception and
        without doing something. More generally the creation date should
        always been younger than the entries' dates.
        But what if we want generate one inventory the same day after we have
        finished to build all products? Use time-date in place of day?
        As security we can require that the 'Arrivage' date should be used
        for the entries.
        TODO: what about 'Sortie' dates?
        """
        d1 = date(2017, 3, 1)
        creation_date = date(2017, 2, 1) # Inventory creation date
        self.do_E(d1, 'a1', 4)
        self.assertRaises(BadCreationDateException, Inventory.sum_entries, creation_date)
        # Test the limit case where creation is the same as the oldest 'Entree'.
        creation_date = date(2017, 3, 1)
        self.assertRaises(BadCreationDateException, Inventory.sum_entries, creation_date)
        
        

    def test_case02(self):
        """ If another inventory is generated with the same creation date
        the inventory entries are updated. A new one is not added. For security
        the Inventory model has a constraint "unique".
        """
        d1 = date(2017, 1, 3) 
        creation_date = date(2017, 2, 1) # Inventory creation date
        self.do_E(d1, 'a1', 4)
        Inventory.sum_entries(creation_date)  
        a1_count = Inventory.get_quantity(self.get_art('a1'), d1, creation_date)      
        self.assertEqual(4, a1_count)
        Inventory.sum_entries(creation_date)
        a1_count = Inventory.get_quantity(self.get_art('a1'), d1, creation_date)      
        self.assertEqual(4, a1_count)
        
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
        creation_date = date(2017, 2, 1) # Inventory creation date
        self.do_E(d1, 'a1', 4)
        a1 = self.get_art('a1') # getting the 'Article' instance with key 'a1'.
        a1_count = Inventory.get_quantity(a1, self.start_date, end_date=d2)
        # The inventory is not yet created then no entry in 
        # inventory exist. 
        self.assertEqual(0, a1_count)
        # But we created one Entree, then the quantity of a1 should be 4.
        self.assertEqual(4, a1.get_quantity())
        # An inventory is generated, using the current date
        Inventory.sum_entries(creation_date)
        self.assertTrue(Inventory.objects.count() == 1)
        # The entry of inventory should be right. 
        # But the generated entry of the inventory is current date.
        # As a result the get_quantity must use the current date to find
        # result.
        a1_count = Inventory.get_quantity(a1, self.start_date, end_date=date.today())
        self.assertEqual(4, a1_count)
        # If we try to get the inventory of last year, which does not exist,
        # we should get zero.
        a1_qte_lastyear = Inventory.get_quantity(a1, 
                                                   date(year=2016, month=1, day=1),
                                                   date(year=2016, month=12, day=31))
        self.assertEqual(0, a1_qte_lastyear)
        # The same holds for dates after the inventory creation date: 1st feb 2017
        start_date = date(year=2017, month=2, day=2) # 2nd february 2017
        end_date   = date(year=2017, month=3, day=31)
        a1_count_future = Inventory.get_quantity(a1, start_date, end_date)
        self.assertEqual(0, a1_count_future)
        
        self.do_S(d2, 'a1', 2)
        self.assertEqual(2, a1.get_quantity())
        # But in inventory the quantity is still 4.
        self.assertEqual(4, Inventory.get_quantity(a1, self.start_date, date.today()))
        Inventory.sum_entries(creation_date = date(2017, 3, 1)) # generate inventory
        # After update of inventory:
        self.assertEqual(2, Inventory.get_quantity(a1, self.start_date, date.today()))
        self.do_S(d2, 'a1', 2)
        self.assertEqual(0, a1.get_quantity())
        # But the quantity of Inventory is still the old one:
        self.assertEqual(2, Inventory.get_quantity(a1, self.start_date, date.today()))
        
        

                
    def prepare_case1(self):
        """ Prepare to test the inventory for a given month.
        We have entries for january and february and want
        the inventory for january only, but we generate
        the inventory in february and in january too.
        """
        d1 = date(2017, 1, 1)
        d2 = date(2017, 1, 2)
        d3 = date(2017, 1, 15)
        d4 = date(2017, 1, 25)
        d5 = date(2017, 1, 28)
        
        self.do_E(d1, 'a1', 10) 
        self.do_E(d1, 'a2', 20) 
        self.do_E(d1, 'a3', 25) 
        self.do_E(d2, 'a4', 15) 
        self.do_S(d3, 'a4', 1)
        self.do_S(d4, 'a1', 5)
        self.do_S(d4, 'a2', 3)
        self.do_S(d5, 'a3', 5)
        
        # Here are the awaited quantities at 4th february.  
        # a1 and a5 have other values than defined above.  
        self.awaited_qt_jan = {'a1':5, 'a2':17, 'a3':20, 'a4':14, 'a5':0}
    
    def test_case1(self):
        """ Goal:
        1. Entrées et sorties faites en janvier et février. 
        2. Génération d'un inventaire.
        3. Sélection des données pour janvier seulement. 
        """
        d1 = date(2017, 1, 1)
        d2_end_jan = date(2017, 1, 31)
        d3_end_fev = date(2017, 2, 28)
        
        self.prepare_case1() # Entrées créées en janvier uniquement.
        # generate inventory at the 31.01.2017
        Inventory.sum_entries(d2_end_jan)       

        self.validate_values(self.awaited_qt_jan)
         
        # February
        d6 = date(2017, 2, 2)
        d7 = date(2017, 2, 4)
        self.do_E(d6, 'a1', 10)
        self.do_E(d7, 'a5', 8) 
        
        # Generate new inventory with the same creation date!
        Inventory.sum_entries(d3_end_fev)
        self.awaited_qt_all = {'a1':15, 'a2':17, 'a3':20, 'a4':14, 'a5':8}
        self.validate_values(self.awaited_qt_all)
            
             
    def prepare_case2(self):
        """ 
        """
        d1 = date(2017, 1, 1)
        d2 = date(2017, 1, 2)
        d3 = date(2017, 1, 15)
        d4 = date(2017, 1, 25)
        d5 = date(2017, 1, 28)
        d6 = date(2017, 2, 2)
        d7 = date(2017, 2, 4)
        self.do_E(d1, 'a1', 10) 
        self.do_E(d1, 'a2', 20) 
        self.do_E(d1, 'a3', 25) 
        self.do_E(d2, 'a4', 15) # soutien-gorge
         
        self.do_S(d3, 'a4', 1)  # soutien-gorge
        
        self.do_E(d3, 'a5', 10)
        
        self.do_S(d4, 'a1', 5)
        self.do_S(d4, 'a2', 3)
        self.do_S(d5, 'a3', 5)
        self.do_S(d5, 'a5', 5)
        
        self.do_E(d6, 'a1', 10)
        self.do_E(d7, 'a5', 8)      
        self.awaited_qt = {'a1':15, 'a2':17, 'a3':20, 'a4':14, 'a5':13}   
        
    def test_case2(self):
        self.prepare_case2()
        Inventory.sum_entries(date(2017, 4, 30))
        self.validate_values(self.awaited_qt)

        
    def do_ES(self, cls, date, a, qte):
        if cls == Entree:
            self.do_E(date, a, qte)
        else:
            self.do_S(date, a, qte)
             
    def prepare_case3(self):
        "Two entries same article same date"
        d1 = date(2017, 1, 1)
        d2 = date(2017, 1, 2)
        d3 = date(2017, 1, 15)
        d4 = date(2017, 1, 25)
        d5 = date(2017, 1, 28)
        d6 = date(2017, 2, 2)
        d7 = date(2017, 2, 4)
        self.do_ES(Entree, d1, 'a1', 10) 
        self.do_ES(Entree, d1, 'a1', 10) # same date, 2 entries of a1 
        self.do_ES(Entree, d1, 'a2', 20) 
        self.do_ES(Entree, d1, 'a3', 25) 
        self.do_ES(Entree, d2, 'a4', 15) 
        self.do_ES(Sortie, d3, 'a4', 1)
        self.do_ES(Entree, d3, 'a5', 10)
        self.do_ES(Sortie, d4, 'a1', 5)
        self.do_ES(Sortie, d4, 'a2', 3)
        self.do_ES(Sortie, d5, 'a3', 5)
        self.do_ES(Sortie, d5, 'a5', 5)
        self.do_ES(Entree, d6, 'a1', 10)
        self.do_ES(Entree, d7, 'a5', 8)      
        self.awaited_qt = {'a1':25, 'a2':17, 'a3':20, 'a4':14, 'a5':13}

    def validate_values(self, awaited_qt):
        for a in awaited_qt.keys():
            awqt = awaited_qt[a]
            aqt  = Inventory.get_last_quantity(2017, self.articles_li[a])
            self.assertEquals(awqt, aqt)
         
    def test_case3(self):
        self.prepare_case3()
        Inventory.sum_entries(date(2017,3,1))
        self.validate_values(self.awaited_qt)

    def btest_case4(self):
        " Simple entries added."
        d1 = date(2017, 1, 1)
        d6 = date(2017, 2, 2)
        self.do_ES(Entree, d1, 'a1', 10) 
        self.do_ES(Entree, d6, 'a1', 10)
        awaited_qt = 20
        total = Inventory.objects.all()
        self.assertEqual(len(total), 0)
        a1 =  self.articles_li['a1']
        Inventory.sum_entries()
        i_a = Inventory.objects.get(article=a1)
        self.assertEqual(i_a.quantity, awaited_qt)
            
    def btest_case5(self):
        " Doubled date entry"
        d1 = date(2017, 1, 1)
        d4 = date(2017, 1, 25)
        d6 = date(2017, 2, 2)
        self.do_ES(Entree, d1, 'a1', 10)
        self.do_ES(Entree, d1, 'a1', 10)     
        self.do_ES(Entree, d6, 'a1', 10)
        awaited_qt = 30
        a1 =  self.articles_li['a1']
        Inventory.sum_entries()
        i_a = Inventory.objects.filter(article=a1).latest('date')
        self.assertEqual(i_a.quantity, awaited_qt)
         
    def btest_case6(self):
        " Doubled Sortie"
        d1 = date(2017, 1, 1)
        d4 = date(2017, 1, 25)
        d6 = date(2017, 2, 2)
        self.do_ES(Entree, d1, 'a1', 10)
        self.do_ES(Entree, d1, 'a1', 10)
        self.do_ES(Sortie, d4, 'a1', 3)
        self.do_ES(Sortie, d4, 'a1', 3)  
        self.do_ES(Entree, d6, 'a1', 10)
        awaited_qt = 24
        a1 =  self.articles_li['a1']
        Inventory.sum_entries()
        i_a = Inventory.objects.filter(article=a1).latest('date')
        self.assertEqual(i_a.quantity, awaited_qt)
     
    def prepare_case7(self):
        d1 = date(2017, 1, 1)
        d2 = date(2017, 1, 2)
        d3 = date(2017, 1, 15)
        d4 = date(2017, 1, 25)
        d5 = date(2017, 1, 28)
        d6 = date(2017, 2, 2)
        d7 = date(2017, 2, 4)
        self.do_ES(Entree, d1, 'a1', 10) 
        self.do_ES(Entree, d1, 'a2', 20) 
        self.do_ES(Entree, d1, 'a3', 25) 
        self.do_ES(Entree, d2, 'a4', 15)
        self.do_ES(Sortie, d2, 'a3', 5) 
        self.do_ES(Entree, d3, 'a5', 10)
        self.do_ES(Entree, d6, 'a1', 10)
        self.do_ES(Sortie, d6, 'a1', 5)
        self.do_ES(Entree, d7, 'a5', 8)
        # Il faut noter que cela efface toutes les entrées de la date d7!!!
        Entree.objects.filter(date=d7, exemplaire__article=self.articles_li['a5']).delete()    
        self.awaited_qt = {'a1':15, 'a2':20, 'a3':20, 'a4':15, 'a5':10}  
        Inventory.sum_entries()
          
    def btest_case7(self):
        """ Delete one Entree before generating inventory.
        Il faut noter que cela efface toutes les entrées de la date d7!!!
        """
        self.prepare_case7()
        self.do_validation()
         
         
    def prepare_case8_1(self):
        d1 = date(2017, 1, 1)
        d2 = date(2017, 1, 2)
        d3 = date(2017, 1, 15)
        
        
        self.do_ES(Entree, d1, 'a1', 10) 
        self.do_ES(Entree, d1, 'a2', 20) 
        self.do_ES(Entree, d1, 'a3', 25) 
        self.do_ES(Entree, d2, 'a4', 15)
        self.do_ES(Sortie, d2, 'a3', 5) 
        self.do_ES(Entree, d3, 'a5', 10)
        
        awaited_qt_inv1 = {'a1':10, 'a2':20, 'a3':20, 'a4':15, 'a5':10}
        # we generate one inventory at the end of the month: 31.01.2017
         
        Inventory.sum_entries(start_date=date(2017, 1, 1),
                              end_date=date(2017, 1, 31))
        return awaited_qt_inv1
         
    def prepare_case8_2(self):
        d4 = date(2017, 2, 2)
        d5 = date(2017, 2, 4)
        d6 = date(2017, 2, 8)
        # we add new entries in february
        self.do_ES(Entree, d4, 'a1', 10)
        self.do_ES(Sortie, d5, 'a1', 5)
        self.do_ES(Sortie, d5, 'a2', 3)
        self.do_ES(Entree, d5, 'a5', 8)
        self.do_ES(Sortie, d6, 'a4', 1)
        
        
        awaited_qt_inv2 = {'a1':15, 'a2':17, 'a3':20, 'a4':14, 'a5':18}
        
        # and generate a second inventory
        # Prévoir avec le mois, plus simple
        Inventory.sum_entries(start_date=date(2017, 2, 1),
                              end_date=date(2017, 2, 28))
        return awaited_qt_inv2
        
    def validate_inventory(self, inventory_date, awaited_qt):
        for k in self.articles_li.keys():
            a = self.articles_li[k]
            q = Inventory.objects.filter(date=inventory_date)
            err = "False quantity for '%s'" % k
            if q.count() > 0: 
                inventory = q.get(article=a)
                self.assertEqual(inventory.quantity, awaited_qt[k], err)
            else:
                self.assertEqual(0, awaited_qt[k])
    
    def btest_case8_1(self):
        """ Testing that inventories do not overlap. 
        Checking 1st inventory. 
        """
        awaited_1 = self.prepare_case8_1()
        awaited_2 = self.prepare_case8_2()
        self.validate_inventory(date(2017, 1, 1), awaited_1)
        
    def btest_case8_2(self):
        """ Testing that inventories do not overlap. 
        Checking 2nd inventory. 
        """
        awaited_1 = self.prepare_case8_1()
        awaited_2 = self.prepare_case8_2()
        self.validate_inventory(date(2017, 2, 1), awaited_2)
        
    def zeroes(self, awaited):
        "Helper to reset quantities to zero."
        for k in awaited:
            awaited[k] = 0
        return awaited
        
    def btest_case8_3(self):
        """ Testing there are zero entries before the first
        entry.
        """
        self.prepare_case8_1()
        awaited = self.prepare_case8_2()
        awaited = self.zeroes(awaited)
        # Looking for non-existent inventory of 2016.
        self.validate_inventory(date(2016, 12, 1), awaited)
        
    def btest_exemplaire_yapasphoto(self):
        a1 =  self.articles_li['a1']
        d1 = date(2017, 1, 1)
        e = Exemplaire.objects.create(article=a1, date_entree=d1)
        self.assertEqual(e.date_entree, d1)    
        
    
        
        
        
        
        

