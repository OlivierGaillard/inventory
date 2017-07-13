import datetime
from django.db import models
from django.db.models import Sum
from django.utils import timezone
from coordinates.models import Arrivage
from finance.models import Currency, Frais, Achat, Tarif # imaginable qu'un article génère des frais


# class Article(models.Model):
#     """
#     """
#     clients_choices = (
#         ('H', 'Homme'),
#         ('F', 'Femme'),
#         ('E', 'Enfant'),
#     )
#
#
#     arrivage        = models.ForeignKey(Arrivage, verbose_name='Dernier arrivage', default=Arrivage.objects.last())
#     #type_de_produit = models.ForeignKey(TypeProduit, null=True)
#     modele          = models.CharField(max_length=150, help_text='par exemple: Boston Sid - jet black', default='pas spécifié')
#     prix_achat      = models.OneToOneField(Achat, null=True, blank=True)
#     marque          = models.ForeignKey(Marque, null=True, blank=True, help_text='AllSaints')
#     type_client     = models.CharField(max_length=1, choices=clients_choices, default='F',)
#     precisions      = models.TextField(max_length=200, null=True, blank=True)
#
#
#     def __str__(self):
#         return self.modele
#
#     def get_quantity(self):
#         """ Retourne la quantité en stock.
#         """
#         balance = 0
#         if Entree.objects.filter(article=self.id).exists():
#             e_sum = Entree.objects.filter(article = self.id).aggregate(Sum('quantity'))
#             e_sum = e_sum['quantity__sum']
#             e_sub = 0
#             if Sortie.objects.filter(article=self.id).exists():
#                 e_sub = Sortie.objects.filter(article = self.id).aggregate(Sum('quantity'))
#                 e_sub = e_sub['quantity__sum']
#                 balance = e_sum - e_sub
#             else:
#                 balance = e_sum
#         return balance
#


        
# class Entree(models.Model):
#     date        = models.DateField(default=timezone.now)
#     #exemplaire  = models.OneToOneField(Exemplaire)
#     article     = models.ForeignKey(Article, blank=True, null=True)
#     quantity    = models.PositiveIntegerField(blank=True, null=True)
#
#     def __str__(self):
#         return self.article.modele
#
# class Sortie(models.Model):
#     date        = models.DateField(default=timezone.now)
#     article     = models.ForeignKey(Article, blank=True, null=True)
#     quantity    = models.PositiveIntegerField(blank=True, null=True)
    

class BadCreationDateException(Exception):
    "Raised if the creation date is older than some entries."
    pass
          
class Inventory(models.Model):
    date = models.DateField(default=timezone.now)
    quantity = models.PositiveSmallIntegerField(default=0)
    
    # def __str__(self):
    #     return str(self.date) + ' - ' + str(self.article.genre_article) + ' - ' + str(self.quantity)
    
    class Meta:
        verbose_name_plural = 'Inventories'
        unique_together = (('date', 'article'))
        ordering = ['-date']
        
    def get_entries(start_date, end_date):
        """ Return all entries between start and end_date inclusive 
        If there a more than one entry for one article all entries
        for this article are returned and not only the most recent one.
        """  
        return Inventory.objects.filter(date__range=(start_date, end_date))
    
    def get_year_entries(year):
        "Get all entries of the given year."
        start_date = date(year, 1, 1)
        end_date   = date(year, 12, 31)
        return Inventory.objects.filter(date__range=(start_date, end_date))
        
    def get_quantity(article, start_date, end_date):
        """ Return the quantity of the Inventory for the parameter 'article'
            between the start- and end-date."""
        #print ('Get_quantity: start_date %s / end_date: %s' % (start_date, end_date))
        q = Inventory.get_entries(start_date, end_date)
        if q.filter(article=article).exists():
#             print ('Article %s exists.' % article)
            qte = q.filter(article=article).latest('date').quantity
#             print ('Quantité: %s' % qte)
            return qte
            #return q.filter(article=article).latest('date').quantity
        else:
            #print ('Article %s does not exist.' % article)
            #print(q)
            return 0

    def get_last_quantity(year, article):
        """ Return the last quantity of the Inventory for the parameter 'article'
                between the start- and end-date."""
        q = Inventory.objects.filter(date__year=year)
        if q.filter(article=article).exists():
            qte = q.filter(article=article).latest('date').quantity
            return qte
            # return q.filter(article=article).latest('date').quantity
        else:
            #print('Article %s does not exist.' % article)
            return 0

    def sum_entries(creation_date):
        """ Generate Inventory's entries.
        Get all instances of 'Entree' and aggregate
        them and substract the sum of all 'Sortie' to get the current quantity. 
        The result is one inventory entry pro article, with the creation's date and quantity.
        """
        # Getting the first Entree if any.
        if Entree.objects.all().exists():
#             print('Il y a des entrées.')
            entree = Entree.objects.latest('date')
            if creation_date <= entree.date: 
                raise BadCreationDateException('Des entrées existent plus récentes ou identiques à la date de création.') 
            for a in Article.objects.all():
                #print ('Handling article %s ...' % a)
                balance = 0
                if Entree.objects.filter(article=a).exists():
                    e_sum = Entree.objects.filter(article = a).aggregate(Sum('quantity'))
                    e_sum = e_sum['quantity__sum']
                    e_sub = 0
                    if Sortie.objects.filter(article=a).exists():
                        e_sub = Sortie.objects.filter(article = a).aggregate(Sum('quantity'))
                        e_sub = e_sub['quantity__sum']
                        balance = e_sum - e_sub
                    else:
                        balance = e_sum
                    if Inventory.objects.filter(article=a).exists():
                        inv = Inventory.objects.filter(article=a)[0]
                        inv.quantity = balance
                        inv.save()
                        #print('Updated with value %s' % balance)
                        #print (inv)
                    else:
                        inv = Inventory.objects.create(date=creation_date, article=a, quantity=balance)
                        #print('Created new entry with value %s' % balance)
                        #print (inv)
        else:
            #print("Il n'y a pas d'entrées.")
            pass

            
    
    
