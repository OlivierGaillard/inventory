Reprise en décembre 2017
========================

Impressions
-----------

- Le *design* choisi avec la classe *Product* se révèle, sans
  surprise, peu pratique à reprendre.
- Il y a une confusion, un léger glissement entre les buts d'un
  inventaire et celui d'une gestion.
- L'ajoût d'une vente passe par un clic sur le lien *quantité* d'une
  liste d'un article. C'est pas terriblement parlant mais c'est
  utilisable et suffisant pour un test fonctionnel.

Ajouts tout récents
-------------------

- La liste des arrivages est complétée par des données de gestion
  telles que le coût de revient, le total des ventes et le solde.

Perspective
-----------

Les totaux ajoutés à la liste des arrivages sont valides pendant
combien de temps?

Le processus est le suivant:

1. création d'un arrivage avec frais.
2. ajout des articles liés à cet arrivage (avec photos
   éventuellement). 
3. ajout des ventes manuellement.

En pratique il faut pouvoir relier les articles en magasin avec ceux
qui ont été saisis. Ceci n'est pas possible actuellement car rien
n'est prévu pour imprimer une fiche article ou une étiquette.

Saisir une vente implique de rechercher l'article manuellement en
faisant défiler le contenu (certes par type d'article) ce qui peut
s'avérer impossible si le nombre est trop grand. Il faudra donc
implémenter une recherche, mais avec quels critères?

Le nom du modèle est un critère de choix essentiel mais son ID reste
la solution la plus sûre.

Séparer le module des ventes
----------------------------

Avant de poursuivre avec l'amélioration du processus de vente et de
recherche il faut envisager de séparer le processus de vente, et même
la partie servant à l'analyse.

Il est clair qu'un petit modèle de données ne serait pas de trop!

Question analyse il est possible qu'un ou plusieurs arrivages soient
déficitaires mais que globalement le solde soit positif. Pourvu que
les bénéfices réalisés par tous les arrivages soient suffisants.

Le stock d'un arrivage peut durer jusqu'à son épuisement ou jusqu'à la
liquidation du stock. Cela implique qu'une *sortie* n'est pas
nécessairement liée à un client car la liquidation peut consister à
jeter les invendus invendables! J'imagine aussi facilement la
situation où une centaine d'articles doivent être liquidés: dans cette
version il n'est pas possible de réaliser cette opération facilement:

- aucun scan des étiquettes;
- pas de fonction "liquidation" pour un arrivage (cela présuppose
  qu'il est facile de repérer l'arrivage des articles en magasin);

Il est possible d'implémenter cette partie dans le site d'inventaire
mais clairement il faudrait créer un site dédié à la vente, surtout si
l'on pense à la vente par internet.

De façon générale le module de vente devrait être indépendant de la
façon dont les ventes sont réalisées (par internet ou en magasin). Il
y a aussi une raison pratique concernant aussi la saisie des articles
des arrivages. Il est commercialement valable de prévoir l'usage d'un
mobile pour ces opérations:

1. scan du code-barre ou saisie du no d'article;
2. saisie d'un nouvel article avec envoi des photos.


Dans la version actuelle il faut regrouper tous les arrivages et
saisir les ventes. Mais quand s'arrêter?

Si un nouvel arrivage date de fin décembre, qu'il est saisi en
décembre, il va fausser le résultat du budget de l'an prochain. Il
faut alors lui donner une date de naissance dans le futur. Vraiment?

Vente: connecter le stock
-------------------------

Comment implémenter l'ajoût des articles dans un point de vente ou un
site internet ?


