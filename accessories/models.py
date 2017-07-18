from django.db import models
from django.shortcuts import reverse
from mptt.models import MPTTModel
from mptt.models import TreeManyToManyField, TreeForeignKey
from products.models import Product, Entree, Sortie, Inventory, Marque


class AccessoryCategory(MPTTModel):
    parent = TreeForeignKey('self', blank=True, null=True)
    title  = models.CharField(max_length=200)

    class Meta:
        ordering = ['tree_id', 'lft']
        verbose_name = 'Catégorie accessoire'
        verbose_name_plural = 'Catégories'

    def __str__(self):
        return self.title

class AccessoryMarque(models.Model):
    nom_marque = models.CharField(max_length=80)

    def __str__(self):
        return self.nom_marque

    class Meta:
        ordering = ['nom_marque']

class Accessory(Product):
    categories = TreeManyToManyField(AccessoryCategory, verbose_name='Catégorie accessoire')
    marque_ref = models.ForeignKey(AccessoryMarque, null=True, blank=True, help_text='Choix des marques')

    class Meta:
        verbose_name = 'Accessoire'
        permissions = (
             ("view_achat", "Can view achats"),
        )

    def get_absolute_url(self):
        return reverse('accessories:detail', kwargs={'pk' : self.pk})

    def get_entrees(self):
        return AccessoryEntry.objects

    def get_sorties(self):
        return AccessoryOutput.objects

    def get_marque_class(self):
        """Return the class AccessoryMarque"""
        return AccessoryMarque


class Photo(models.Model):
    photo    = models.ImageField(upload_to = 'accessories', blank=True, null=True)
    legende  = models.CharField(max_length=20, blank=True, null=True)
    article  = models.ForeignKey(Accessory, blank=True, null=True)

    def __str__(self):
        return self.legende


class AccessoryEntry(Entree):
    article = models.ForeignKey(Accessory, blank=True, null=True)

    # def __str__(self):
    #     return self.article.name


class AccessoryOutput(Sortie):
    article = models.ForeignKey(Accessory, blank=True, null=True)

    def __str__(self):
        return self.article.name


class InventoryAccessory(Inventory):
    article = models.ForeignKey(Accessory)

    def get_objects(self):
        return InventoryAccessory.objects

    def get_article(self):
        return Accessory.objects

    def get_entrees(self):
        return AccessoryEntry.objects

    def get_sorties(self):
        return AccessoryOutput.objects

    class Meta(Inventory.Meta):
        unique_together = (('date', 'article'))
