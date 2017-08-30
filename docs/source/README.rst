README
======

Inventory is a project built for helping small stores to manage their inventory.
It is now targeted to fashion and sewing. What is possible in a few points:

* Create arrivals. An arrival is like a shipping for your store. You buy some merchandise.
* Enter revenue costs of one arrival: trip, hotel etc.
* Multiple currencies. The rates are taken from opencurrencies service. The list of currencies allows
  to select which one to use.
* For the currencies they are management script to get all currencies and updating the exchange rates.
  See app *finance.management* and file usage.rst.
* Enter articles: entering one article generate one input with a quantity
* Enter sellings. Entering one selling generates one output, with a quantity.
* Generate inventories. An inventory lists the articles' quantity which is the sum of inputs
  substracted from outputs.
* Up-to-date stock quantity.
* User fine grained permissions: only dedicated user may see revenue costs.
* Multiple enterprises can have their own inventories and stocks management.
* They are management tools to load pre-made categories of products: see the folders *fixtures*
  and *management*.