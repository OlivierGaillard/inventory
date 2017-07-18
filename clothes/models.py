from django.db import models
from django.shortcuts import reverse
from mptt.models import MPTTModel
from mptt.models import TreeManyToManyField, TreeForeignKey
from products.models import Product, Entree, Sortie, Inventory


class ClothesCategory(MPTTModel):
    parent = TreeForeignKey('self', blank=True, null=True)
    title  = models.CharField(max_length=200)

    class Meta:
        ordering = ['tree_id', 'lft']
        verbose_name = 'Catégorie accessoire'
        verbose_name_plural = 'Catégories'

    def __str__(self):
        return self.title


class Clothes(Product):
    categories = TreeManyToManyField(ClothesCategory, verbose_name="Catégorie d'habits")

    class Meta:
        verbose_name = 'Habit'

    def get_entrees(self):
        return ClothesEntry.objects

    def get_sorties(self):
        return ClothesOutput.objects

    def get_absolute_url(self):
        return reverse('clothes:detail', kwargs={'pk' : self.pk})


class Photo(models.Model):
    photo    = models.ImageField(upload_to = 'habits', blank=True, null=True)
    legende  = models.CharField(max_length=20, blank=True, null=True)
    article  = models.ForeignKey(Clothes, blank=True, null=True)

    def __str__(self):
        return self.legende


class ClothesEntry(Entree):
    article = models.ForeignKey(Clothes, blank=True, null=True)

    def __str__(self):
        return self.article.name


class ClothesOutput(Sortie):
    article = models.ForeignKey(Clothes, blank=True, null=True)

    def __str__(self):
        return self.article.name


class InventoryClothes(Inventory):
    article = models.ForeignKey(Clothes)

    def get_objects(self):
        return InventoryClothes.objects

    def get_article(self):
        return Clothes.objects

    def get_entrees(self):
        return ClothesEntry.objects

    def get_sorties(self):
        return ClothesOutput.objects

    class Meta(Inventory.Meta):
        unique_together = (('date', 'article'))

