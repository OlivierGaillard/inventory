User Stories
============

Idéalement
----------

L'utilisateur peut utiliser le site web comme eCommerce avec une
fonction de vente cash: le site devient sa caisse enregistreuse, sert
à imprimer ses tickets de caisses (reçus), factures, enregistrer ses
ventes, voire à quel client, les avances aussi éventuellement. Il peut
aussi générer des rapports de vente. Surtout il doit d'abord pouvoir
entrer ses marchandises: quantité, article, photo, prix d'achat et
prix de vente projeté et effectuer une vente (avec au minimum ce qui a
été vendu (combien d'articles, d'exemplaires, à quel prix, y-a-t-il eu
une remise).

Le prix de vente affiché ne correspond pas nécessairement au prix de
vente final dans le cas d'une vente cash car le client
marchande. C'est spécifique d'une vente en boutique en Afrique. On
affiche un prix toujours supérieur au prix de vente attendu pour
démarrer le marchandage assez haut. Le prix de vente cash n'est donc
pas fixe. Mais les étiquettes des articles exposés en boutique
correspondent au prix pour marchandage; elles ont des valeurs
différentes que celles du site.

Situation début décembre 2017
-----------------------------

Il est possible de:

- créer un arrivage et de lui associer des frais. Le total des frais
  est affiché sur la ligne du tableau listant les arrivages.

- créer des catégories pour 3 types d'articles: des habits, des
  chaussures ou d'accessoires.

- d'afficher et de modifier les catégories.

- de créer un article en spécifiant:

  - son arrivage
  - son nom
  - sa marque (on sélectionne ou on en crée une nouvelle)
  - la quantité achetée
  - le prix payé (en gros ou par article)

- de générer un inventaire pour les trois types d'articles.

A faire
-------

- afficher le total des achats et des frais pour un
  arrivage. Simplement ajouter le total des achats dans le tableau des
  arrivages. 
  
- afficher et calculer le solde d'un arrivage en fonction des ventes
  et des achats avec les frais.

- afficher la prévision du chiffre de ventes requis pour couvrir un
  arrivage selon le bénéfice prévu en pourcentage.

Lister les achats d'un arrivage
-------------------------------

Un arrivage est lié à des frais par le moyen de `FraisArrivage` qui
possède une clé étrangère sur un arrivage. Pour accéder aux frais d'un
arrivage depuis une instance d'arrivage on utilise la syntaxe
`arrivage.fraisarrivage_set.all()`.

Comment accéder au total des prix d'achats d'un arrivage concernant
les articles? Tout article possède une référence à la classe
`finance.Achat`. Mais comment savoir si l'achat est à l'unité ou
global? C'est sans importance à ce stade mais pas lors de la
saisie. Dans ce cas le formulaire demande de choisir si le coût est à
l'unité ou global, et le total est calculé en fonction du choix. A
l'unité? Alors le prix est multiplié par la quantité. Global? Quelle
que soit la quantité le prix enregistré est celui qui a été saisi.

Tout article possède une référence à un arrivage. Donc à partir d'un
arrivage on peut retrouver tous les articles. Ce qui se traduit par
`ar.clothes_set.all()` pour une instance `ar` d'arrivage.

Ensuite on peut faire, si `zue` est une instance de l'arrivage `Zuerich`::

  zue.clothes_set.all()
  <QuerySet [<Clothes: Minitruc / Mikafashion>, <Clothes: Mango / Mikafashion>]>
  >>> for c in zue.clothes_set.all():
  ...     print (c.prix_achat)

