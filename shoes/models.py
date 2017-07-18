from django.db import models
from django.shortcuts import reverse
from mptt.models import MPTTModel
from mptt.fields import TreeForeignKey, TreeManyToManyField
from products.models import Product, Entree, Sortie, Inventory

# Create your models here.

class ShoeCategory(MPTTModel):
    parent = TreeForeignKey('self', blank=True, null=True)
    title  = models.CharField(max_length=200)

    class Meta:
        ordering = ['tree_id', 'lft']
        verbose_name = 'Catégorie'
        verbose_name_plural = 'Catégories'

    def __str__(self):
        return self.title

class Shoe(Product):
    categories = TreeManyToManyField(ShoeCategory, verbose_name='Catégories')

    class Meta:
        verbose_name = 'Chaussures'

    def get_entrees(self):
        return ShoeEntry.objects

    def get_sorties(self):
        return ShoeOutput.objects

    def get_absolute_url(self):
        return reverse('shoes:detail', kwargs={'pk' : self.pk})



class ShoeEntry(Entree):
    article = models.ForeignKey(Shoe, blank=True, null=True)

    def __str__(self):
        return self.article.name

class ShoeOutput(Sortie):
    article = models.ForeignKey(Shoe, blank=True, null=True)

    def __str__(self):
        return self.article.name

class Photo(models.Model):
    photo    = models.ImageField(upload_to = 'shoes', blank=True, null=True)
    legende  = models.CharField(max_length=20, blank=True, null=True)
    article  = models.ForeignKey(Shoe, blank=True, null=True)

    def __str__(self):
        return self.legende

class InventoryShoe(Inventory):
    article = models.ForeignKey(Shoe)

    def get_objects(self):
        return InventoryShoe.objects

    def get_article(self):
        return Shoe.objects

    def get_entrees(self):
        return ShoeEntry.objects

    def get_sorties(self):
        return ShoeOutput.objects

    class Meta(Inventory.Meta):
        unique_together = (('date', 'article'))
