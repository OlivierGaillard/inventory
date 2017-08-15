from django_tables2 import Table
from .models import Vente

class VenteTable(Table):
    class Meta:
        model = Vente
        attrs = {'class' : 'table'}

