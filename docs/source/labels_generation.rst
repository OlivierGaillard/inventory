# Labels Generation

Labels generation can be made with LaTeX, with HTML, with Django packages to write PDF or convert from
HTML to PDF. The requirements are:

1. generate as many labels as the stock quantity.
2. each label must contain the article's type and its ID.
3. the labels can be printed on A4 paper (3 labels per rows, and about 8 rows).

Nice to have:

4. A barcode containing the above infos.

We need probably a dedicated "app" as it make no sense to include it in one or another articles' type app like
"accessories", "clothes" or "shoes".

I created the app "labels". Do I need any specific model? Not sure. Only a view and one template.

## Constructing the table for labels

I will a table with 3 columns, each item itself being a table with the data for one label.
We have:

- one loop over the list of articles
- one inner loop over the quantity of each article

The logic is contained within the inner loop. If the inner loop counter is divisible by
3,  we have reached the end of a row and we close "</tr>".

Otherwise we add one table data element "td".

Let's say we have the list 5 quantity of article ID 3. Then:

(Why not use bootstrap grid system?)

Nous aurons un début de ligne aux valeurs du compteur suivantes:

1, 2, 3
4, 5, 6
7, 8, 9,
10, 11, 12
13, 14, 15

Après chaque multiple de 3 il y a passage à la ligne, ainsi qu'avec 1.

Si le compteur = 1 ou s'il est divisible par 3.

