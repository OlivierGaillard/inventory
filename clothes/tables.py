from django_tables2 import Table, tables
from .models import Clothes

class ClothesTable(tables.Table):
    quantity = tables.columns.Column('quantity', accessor='get_quantity', visible=True)
    class Meta:
        model = Clothes
        attrs = {'class' : 'table'}


