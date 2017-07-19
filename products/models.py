from django.db import models
from django.utils import timezone
from django.db.models import Sum
from coordinates.models import Arrivage
from mptt.models import MPTTModel
from mptt.fields import TreeForeignKey, TreeManyToManyField
from finance.models import Achat

# Create your models here.
class Entree(models.Model):
    # date should be the same as the Arrivage.
    date = models.DateField(default=timezone.now, verbose_name="Date de l'arrivage")
    creation_date = models.DateTimeField(auto_now_add=True, null=True)
    quantity = models.PositiveIntegerField(blank=True, null=True)

    class Meta:
        abstract = True

    def __str__(self):
        s = 'Date: %s\n Creation-date: %s \n Quantity: %s' % (self.date, self.creation_date,
                                                              self.quantity)
        return s

class Sortie(models.Model):
    date        = models.DateField(auto_now=True)
    quantity    = models.PositiveIntegerField(blank=True, null=True)

    class Meta:
        abstract = True


class Marque(models.Model):
    nom_marque = models.CharField(max_length=80)

    def __str__(self):
        return self.nom_marque


class Category(MPTTModel):
    parent = TreeForeignKey('self', blank=True, null=True)
    title  = models.CharField(max_length=200)

    class Meta:
        abstract = False
        ordering = ['tree_id', 'lft']
        verbose_name = 'Catégorie'
        verbose_name_plural = 'Catégories'

    def __str__(self):
        return self.title


class BadCreationDateException(Exception):
    "Raised if the creation date is older or equal than some entries."
    pass

class Inventory(models.Model):
    date = models.DateField(default=timezone.now)
    # article = models.ForeignKey(Product)
    quantity = models.PositiveSmallIntegerField(default=0)

    class Meta:
        abstract = True
        verbose_name_plural = 'Inventories'
        # unique_together = (('date', 'article'))
        ordering = ['-date']

    def __str__(self):
        return str(self.date) + ' - ' + str(self.article.name) + ' - ' + str(self.quantity)


    def get_objects(self):
        "Return the objects of the concrete Inventory: InventoryShoe, InventoryClothes or InventoryAccessory."
        raise NotImplementedError('Abstract "Inventory" class waits that its children implement a method returning concrete Inventory objects!')

    def get_article(self):
        "Return the concrete instance: Clothes, Shoe or Accessory"
        raise NotImplementedError('Abastract "Inventory" waits that its children implement a method returning concrete article e.g. Shoe.objects!')

    def get_entrees(self):
        "Return the concrete Entree: ClothesEntry, AccessoryEntry."
        raise NotImplementedError('Children classes of "Inventory" have to implement a method returning Entry objects!')

    def get_sorties(self):
        "Return the concrete Sortie: ClothesOutput, AccessoryOutput"
        raise NotImplementedError('Children classes of "Inventory" have to implement a method returning Output objects!')



    def sum_entries(self, creation_date):
        """ Generate Inventory's entries.
        Get all instances of 'Entree' and aggregate
        them and substract the sum of all 'Sortie' to get the current quantity.
        The result is one inventory entry pro article, with the creation's date and quantity.
        """
        # Getting the first Entree if any.
        #print('In products-app Inventory-sum_entries')
        if self.get_entrees().all().exists():
            #print('Il y a des entrées.')
            #entree = self.get_entrees().latest('date')
            # if creation_date <= entree.date:
            #     raise BadCreationDateException(
            #         'Des entrées existent plus récentes ou égales à la date de création. Probablement la date du jour. ')
            for a in self.get_article().all():
                #print ('Handling article %s ...' % a)
                balance = 0
                if self.get_entrees().filter(article=a).exists():
                    e_sum = self.get_entrees().filter(article=a).aggregate(Sum('quantity'))
                    e_sum = e_sum['quantity__sum']
                    e_sub = 0
                    if self.get_sorties().filter(article=a).exists():
                        e_sub = self.get_sorties().filter(article=a).aggregate(Sum('quantity'))
                        e_sub = e_sub['quantity__sum']
                        balance = e_sum - e_sub
                    else:
                        balance = e_sum
                    if self.get_objects().filter(article=a).exists():
                        inv = self.get_objects().filter(article=a)[0]
                        inv.quantity = balance
                        inv.save()
                        #print('Updated with value %s' % balance)
                        #print (inv)
                    else:
                        inv = self.get_objects().create(date=creation_date, article=a, quantity=balance)
                        #print('Created new entry with value %s' % balance)
                        #print (inv)
        else:
            pass
            #print("Il n'y a pas d'entrées.")
            #pass
        #print('End of Inventory sum_entries job.')

    def get_entries(self, start_date, end_date):
        """ Return all entries between start and end_date inclusive
        If there a more than one entry for one article all entries
        for this article are returned and not only the most recent one.
        """
        objects = self.get_objects()
        return objects.filter(date__range=(start_date, end_date))

    def get_year_entries(self, year):
        "Get all entries of the given year."
        start_date = date(year, 1, 1)
        end_date = date(year, 12, 31)
        return self.get_objects().filter(date__range=(start_date, end_date))

    def get_quantity(self, article, start_date, end_date):
        """ Return the quantity of the Inventory for the parameter 'article'
            between the start- and end-date."""
        # print ('Get_quantity: start_date %s / end_date: %s' % (start_date, end_date))
        q = self.get_entries(start_date, end_date)
        if q.filter(article=article).exists():
            #             print ('Article %s exists.' % article)
            qte = q.filter(article=article).latest('date').quantity
            #             print ('Quantité: %s' % qte)
            return qte
        else:
            # print ('Article %s does not exist.' % article)
            return 0

    def get_last_quantity(year, article):
        """ Return the last quantity of the Inventory for the parameter 'article'
                between the start- and end-date."""
        q = Inventory.objects.filter(date__year=year)
        if q.filter(article=article).exists():
            qte = q.filter(article=article).latest('date').quantity
            return qte
        else:
            # print('Article %s does not exist.' % article)
            return 0



class Product(models.Model):

    class Meta:
        abstract = True


    clients_choices = (
        ('H', 'Homme'),
        ('F', 'Femme'),
        ('E', 'Enfant'),
    )
    type_client = models.CharField(max_length=1, choices=clients_choices, default='F', )
    #categories = TreeManyToManyField(Category, verbose_name='Catégories')
    name = models.CharField(max_length=100, verbose_name='Nom du modèle')
    marque_ref = models.ForeignKey(Marque, null=True, blank=True, help_text='Choix des marques')
    arrivage = models.ForeignKey(Arrivage, null=True)
    prix_achat = models.OneToOneField(Achat, null=True, blank=True, verbose_name="Prix d'achat unitaire")
    date_ajout = models.DateField(auto_created=True, default=timezone.now)

    def __str__(self):
        return self.name

    def get_entrees(self):
        raise NotImplementedError('Children classes of "Product" have to implement a method returning Entree objects!')

    def get_sorties(self):
        raise NotImplementedError('Children classes of "Product" have to implement a method returnin Sortie objects!')

    def get_quantity(self):
        """ Retourne la quantité en stock.
        """
        entrees = self.get_entrees()
        sorties = self.get_sorties()
        balance = 0
        if entrees.filter(article=self.id).exists():
            #print("There are entries.")
            e_sum = entrees.filter(article = self.id).aggregate(Sum('quantity'))
            e_sum = e_sum['quantity__sum']
            if sorties.filter(article=self.id).exists():
                e_sub = sorties.filter(article = self.id).aggregate(Sum('quantity'))
                e_sub = e_sub['quantity__sum']
                balance = e_sum - e_sub
            else:
                balance = e_sum
        else:
            pass
            #print("There are no entries.")
        return balance


    def get_marque_class(self):
        """Can be implemented by the concrete class if it has its own Marque"""
        raise NotImplementedError('Children classes of "Product" can implement get_marque_class')

    def update_marque_ref(self, marque, marque_ref):
        """Update the foreign key to marque, eventually creates a new Marque."""
        try:
            cls_marque = self.get_marque_class()
        except NotImplementedError:
            cls_marque = Marque
        if marque and len(marque) > 0:
            if not cls_marque.objects.filter(nom_marque=marque).exists():
                new_marque = cls_marque.objects.create(nom_marque=marque)
                self.marque_ref = new_marque
                self.save()
#                print("New marque '", new_marque, "' created.")
        else:
             self.marque_ref = cls_marque.objects.get(pk=marque_ref)
             self.save()



