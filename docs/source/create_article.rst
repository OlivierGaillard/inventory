Processus to create one article
=====================================

Prerequisites
-------------

1) The user is created

2) She is an employee of one enterprise

   a) One instance of Enterprise is created.

   b) One instance of Employee is created.

3) One instance of Arrivage is created with a foreign key to the enterprise.

Description of the fields
-------------------------


With the previous points in place it possible to create one article with the minimal
following attributes. It is the tab *Fiche article* :

   a) name

   b) select one arrival

   c) product owner is a information readonly field taken from employee

   d) quantity

   The *classification* tab allows to enter:

   a) type_client: for man, woman or children.

   b) to select one category e.g. *t-shirt* or *chaussettes*.

   d) to select an existing *marque* or enter a new one


Once the above is done you can enter the purchase amount (in french *prix d'achat*) and add pictures.

Edit one article
----------------

purchase type
  Did you pay per unit or did you pay for the set? If you select *per unit* the price will be
  multiplied by the quantity.

devise
  The currency used for the purchase. In the articles listing, contrary to the arrivals' costs, it is not
  possible to change the currency. Due to rate changes it is not clear if this possibility is
  good or not.







