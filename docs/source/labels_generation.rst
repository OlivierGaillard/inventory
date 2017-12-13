# Labels Generation

The requirements are:

1. generate as many labels as the stock quantity.
2. each label must contain the article's type and its ID.
3. the labels can be printed on A4 paper (3 labels per rows, and about 8 rows).

Nice to have:

4. A barcode containing the above infos.

We need probably a dedicated "app" as it make no sense to include it in one or another articles' type app like
"accessories", "clothes" or "shoes".


## Implementation

Finally I choosed to generate a LaTeX source and produce a PDF with it. I used the
LaTeX package `labels`. It is a little bit obsolete but a lot simpler to use than
HTML and CSS. DjangoEurope included this package per default.

## Other tempatives

Trying to print the labels generated with a custom CSS failed a little bit because the
background color of the lables was not printable, even by adding a Google chrome extension.
As this problem depends on the browser setting it is a lot better to generate a PDF.


- Install django-easy-pdf
- Intall WeasyPrint


Installing "cairocffi" failed for unknown reason. Then I wonder what to do Options are:

- trying to install to find that DjangoEurope has not this library?
- generate one LaTeX source file (and the package is not installed on DjangoEurope?)

### Package `django-hardcopy`

Ce package nécessite `chromium`.

The result was deceiving.

I created the app "labels". Do I need any specific model? Not sure. Only a view and one template.

