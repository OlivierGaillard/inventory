from django_tables2 import Table, tables, columns
from django_tables2.utils import A
from .models import Vente, Achat

class VenteTable(tables.Table):
    article = tables.columns.Column('Article', accessor='article', orderable=False)
#    montant = tables.columns.Column('Montant', accessor='montant')
    product_id = tables.columns.Column('product_id', accessor='product_id', visible=False)
    #id = tables.columns.Column('No', visible=True)
    product_owner = tables.columns.Column('product_owner', visible=False)
    client_id = tables.columns.Column('Client', accessor='client_id')
    #edit_vente = tables.columns.LinkColumn("finance:update_vente", args=[A('pk')])
    id = tables.columns.LinkColumn("finance:update_vente", args=[A('pk')])
    class Meta:
        model = Vente
        attrs = {'class' : 'table'}


class AchatTable(tables.Table):
    article = tables.columns.Column('Article', accessor='article', orderable=False)
    product_id = tables.columns.Column('product_id', accessor='product_id', visible=True)
    product_owner = tables.columns.Column('product_owner', visible=True)


    class Meta:
        model = Achat
        attrs = {'class' : 'table'}



