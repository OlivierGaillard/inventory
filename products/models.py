from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from django.db.models import Sum
from coordinates.models import Arrivage
from mptt.models import MPTTModel
from mptt.fields import TreeForeignKey
import logging

logger = logging.getLogger('django')


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
    """
    Abstract model to generate inventories returning the stock quantity of each article.

    Explanation:
      One inventory is dated. It is generated at a given date entered by the user, but this
      date is not taken into account for the inventory because all entries and outputs are
      used.

      There is one inventory per article's type (accessory, clothes or shoes).

      TODO: filter the inventories by a given date in order to display only a range or only
      one inventory.

    Implementation:
      The concrete models (InventoryAccessory, InventoryClothes, InventoryShoe) must provide
      the implementation of get_objects, get_entrees and get_sorties.


    """
    date = models.DateField(default=timezone.now)
    # article = models.ForeignKey(Product)
    quantity = models.PositiveSmallIntegerField(default=0) # Total of entries
    enterprise_of_current_user = None  # Will be set when instanciated by the form's method generate_inventory

    def set_enterprise_of_current_user(self, enterprise):
        """
        This method is used by the concrete inventory class (e.g. InventoryAccessory).
        The view (e.g. InventoryCreationView) calls the form's method 'generate_inventory'
        with the param enterprise. And the form (e.g. 'InventoryAccessoryForm') instanciate
        e.g. InventoryAccessory and set the enterprise before calling the 'sum_entries'
        method which will generate the inventory.
        :param enterprise:
        """
        self.enterprise_of_current_user = enterprise


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
        """
        Generate Inventory's entries.

        Get all instances of 'Entree' and aggregate them and substracts
        the sum of all 'Sortie' to get the current quantity.

        The result is one inventory entry pro article, with the creation's date and quantity.
        """
        if self.get_entrees().all().exists(): # all articles of all enterprises
            for a in self.get_article().all(): # Concrete class returns only articles of user's enterprise.
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
                    else:
                        inv = self.get_objects().create(date=creation_date, article=a, quantity=balance)


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

class Enterprise(models.Model):
    """
    Owner of the products.

    This will allow multiple enterprise to use the application.

    Possible implementations are:

    1. the users will belong to an enterprise and have a corresponding
    foreign key.

    2. the enterprise is bound to a group whose name is the one of the user.
    (Seems too complicated and too magic).
    """
    name = models.CharField(max_length=80)


    def __str__(self):
        return self.name

class Employee(models.Model):
    """
    Every user is an employee of one enterprise.

    The articles tables (derived from Product: Accessory, Clothes and Shoe)
     are bound to one enterprise with the help of the foreign key 'Product.product_owner'

    One user may work only with the articles belonging to his/her enterprise.

    The belonging of this user to the enterprise is expressed with the
    foreign key 'Employee.enterprise'.

    Conclusion: the employee has access permission only to the articles of her enterprise.

    Process to create one employee:

    a) create one user
    b) create one enterprise
    c) create one Employee with foreign keys to user and enterprise
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    enterprise = models.ForeignKey(Enterprise, null=True) # To allow smooth migration.

    def get_enterprise_of_current_user(user):
        """
        A class helper method used by the abstract products.forms.ProductCreateForm.
        :param user: the request.user used to retrieve one Employee instance.
        :return: the Enterprise instance of the Employee instance.
        """
        if Employee.objects.filter(user=user).exists():
            employee = Employee.objects.get(user=user)
            return employee.enterprise

    def is_current_user_employee(user):
        if Employee.objects.filter(user=user).exists():
            employee = Employee.objects.get(user=user)
            return employee.enterprise != None
        else:
            return False


    def __str__(self):
        if self.enterprise is not None:
            return self.user.username + ': ' + str(self.enterprise)
        else:
            return self.user.username


class Product(models.Model):


    class Meta:
        abstract = True


    clients_choices = (
        ('H', 'Homme'),
        ('F', 'Femme'),
        ('E', 'Enfant'),
    )
    type_client = models.CharField(max_length=1, choices=clients_choices, default='F', )
    product_owner = models.ForeignKey(Enterprise, default=1)
    name = models.CharField(max_length=100, verbose_name='Nom du modèle')
    marque_ref = models.ForeignKey(Marque, null=True, blank=True, help_text='Choix des marques')
    arrivage = models.ForeignKey(Arrivage, null=True)
    prix_achat = models.OneToOneField('finance.Achat', null=True, blank=True, verbose_name="Prix d'achat global")
    date_ajout = models.DateField(auto_created=True, default=timezone.now)


    def __str__(self):
        return self.name + ' / ' + str(self.product_owner)

    def get_entrees(self):
        raise NotImplementedError('Children classes of "Product" have to implement a method returning Entree objects!')

    def get_sorties(self):
        raise NotImplementedError('Children classes of "Product" have to implement a method returnin Sortie objects!')

    def get_quantity(self):
        """ Retourne la quantité en stock.
        """
        entrees = self.get_entrees()
        logger.debug('total des entrées: %s' % entrees.count())
        logger.debug('Liste de entrées avec quantité:')
        for e in entrees.all():
            logger.debug(e.quantity)
        logger.debug('fin de la liste.')
        sorties = self.get_sorties()
        balance = 0
        if entrees.filter(article=self.id).exists():
            #print("There are entries.")
            e_sum = entrees.filter(article = self.id).aggregate(Sum('quantity'))
            logger.debug("Quantité des entrées: %s" % e_sum)
            e_sum = e_sum['quantity__sum']
            if sorties.filter(article=self.id).exists():
                logger.debug("Des sorties existent.")
                e_sub = sorties.filter(article = self.id).aggregate(Sum('quantity'))
                e_sub = e_sub['quantity__sum']
                logger.debug("Quantité sorties: %s" % e_sub)
                balance = e_sum - e_sub
                logger.debug("e_sum - e_sub = %s" % balance)
            else:
                balance = e_sum
        else:
            logger.debug("Il n'y a pas d'entrées.")
        logger.debug('quantité en stock: %s' % balance)
        return balance

    def get_quantity_as_list(self):
        """Helper for template to print labels."""
        quantity = self.get_quantity()
        return list(range(1, quantity+1))


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


