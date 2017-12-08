from django_tables2 import Table, tables
from .models import Vente

class VenteTable(tables.Table):
    article = tables.columns.Column('Article', accessor='article', orderable=False)
#    montant = tables.columns.Column('Montant', accessor='montant')
    product_id = tables.columns.Column('product_id', accessor='product_id', visible=False)
    id = tables.columns.Column('No', visible=True)
    product_owner = tables.columns.Column('product_owner', visible=False)
    client_id = tables.columns.Column('Client', accessor='client_id')

    class Meta:
        model = Vente
        attrs = {'class' : 'table'}

