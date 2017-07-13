from selenium import webdriver
from selenium.webdriver.support.ui import Select

from django.test import LiveServerTestCase
from django.test import TransactionTestCase
from django.conf import settings

import unittest
from datetime import datetime, timedelta
from django.utils import timezone
from _datetime import date
import locale
import time
from finance.models import Currency
from coordinates.models import Arrivage

class NewVisitorTest(LiveServerTestCase):

    def setUp(self):
        self.browser = webdriver.Firefox()
        self.base_url = self.live_server_url
        #self.browser.implicitly_wait(3)
        odie = datetime.now()
        mytzinfo = timezone.get_current_timezone()
        self.odie = timezone.make_aware(odie, mytzinfo)
        self.odie_str = datetime.strftime(self.odie,'%d-%m-%Y')
        self.heri = self.odie - timedelta(days=1)
        locale.setlocale(locale.LC_ALL, "fr_CH.utf8")
        self.heri_fullMonth = datetime.strftime(self.heri,'%d %B %Y')
        self.heri_str = datetime.strftime(self.heri,'%d-%m-%Y')

        Currency.objects.create(currency_code='CHF', rate_usd=0.9981)

        

    def tearDown(self):
        self.browser.quit()
        #self.invh_heri.delete()

    def test_create_Arrivages(self):
        """ User can create an arrivage.
        """
        self.browser.get(self.live_server_url)
        link_elem = self.browser.find_element_by_partial_link_text('Arrivages')
        self.assertEqual(link_elem.text, 'Arrivages', "Lien 'Arrivages' pas trouvé!")
        url = '/coordinates/arrivage-create/'
        self.browser.get(self.live_server_url + url)
        dateinput = self.browser.find_element_by_id('id_date')
        dateinput.send_keys('2017-01-10')
        designation= self.browser.find_element_by_id('id_designation')
        designation.send_keys("From London in January")

        devises = Select(self.browser.find_element_by_id('id_devise'))
        print(devises.options)
        print([o.text for o in devises.options])
        devises.select_by_visible_text('CHF')
        designation.submit()
        #submit_btn =  self.browser.find_element_by_id('id_submit')   #self.browser.find_element_by_value('Submit')
        time.sleep(10)
        #submit_btn.click()
        # Checking if the arrivage was created
        self.assertEqual(1, Arrivage.objects.all().count(), "No Arrivage was created in DB.")
        url = '/coordinates/arrivages/'
        self.browser.get(self.live_server_url + url)
        h1 = ' <h1>Arrivages</h1>'
        #self.assertIn(h1, self.browser.page_source, "Pas trouvé le titre h1 Arrivages")
        #time.sleep(2)
        #self.assertIn('January', self.browser.page_source, "Pas trouvé l'arrivage 'From London in January'")


    def btest_can_view_list_of_inventaires(self):
        """ User can see the page with the list of inventaires. Each
        inventaire contains a unique field: the date.
        """
        self.browser.get(self.live_server_url)
        ## The click() method does not function, In place I use "send_keys".
        self.browser.find_element_by_partial_link_text('Liste des').send_keys("\n")
        self.browser.get(self.live_server_url + "/inventaires/")
        self.assertIn('Date', self.browser.page_source, "Pas d'accès à la page listant les inventaires par leur date.")

    def btest_can_access_create(self):
        """ User can access the form to create one new inventory.
        """
        self.browser.get(self.live_server_url + '/createinventaire/')
        self.assertIn('nouvel inventaire', self.browser.page_source)
        inputbox = self.browser.find_element_by_id('id_new_inventaireh')
        self.assertEqual(inputbox.get_attribute('value'), self.odie_str)
        # She accepts the today default date
        # When she hits enter, the page updates and the new list
        # of inventaires is displayed.
        submit_button = self.browser.find_element_by_name('submit_button')
        submit_button.click()
        time.sleep(2) ## A required waiting time; otherwise it fails.
        # Checking that the inventaire_header has been created by looking in DB
        invh_list = InventaireHeader.objects.all()
        self.assertTrue(len(invh_list) == 1, "No InventaireHeader instance created.")
        url = self.live_server_url + '/inventaires/'
        self.browser.get(url)
        self.assertIn(self.odie_str, self.browser.page_source)
            
    def btest_can_add_article_to_empty_inventaire(self):
        """ User can add articles to one inventaire. """
        ## Create one inventaire header with date of yesterday.
        self.invh_heri = InventaireHeader(date=self.heri)
        self.invh_heri.save()
        # User creates one empty inventaire-header (TODO)
        
        # User accesses the list of inventories.
        self.browser.get(self.live_server_url + '/inventaires')
        # She select the one of today
        link = self.browser.find_element_by_partial_link_text(self.heri_str)
        self.browser.get(link.get_property("href"))        
        h1 = self.browser.find_element_by_tag_name('h1')
        self.assertIn(self.heri_fullMonth, h1.text)
        
        name_field = self.browser.find_element_by_id('id_new_inventory_item')
        # She adds 10 robes.
        name_field.send_keys('robe')
        quantity_field = self.browser.find_element_by_id('id_inventory_quantity')
        quantity_field.send_keys('10')
        time.sleep(2)
        # And click the "Add" button
        add_article_button = self.browser.find_element_by_name('add_article').click()
        time.sleep(4)
        # Returning to main page
        self.browser.get(self.live_server_url + '/inventaires')
        time.sleep(2)
        # She select the one of today
        link = self.browser.find_element_by_partial_link_text(self.heri_str)
        url = link.get_property("href") + '/'
        print(url)
        self.browser.get(url)
        
        time.sleep(2)
        # The page is refreshing and the new item is displayed.
        self.assertIn('robe', self.browser.page_source)
        
        
    def btest_can_delete_inventaire(self):
        self.assertFalse(2 == 2, "Write deletion of inventaire.")


