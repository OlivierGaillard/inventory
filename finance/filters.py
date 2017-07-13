import django_filters
from .models import FraisArrivage


class FraisArrivageFilter(django_filters.FilterSet):

    class Meta:
        model = FraisArrivage
        fields = ['arrivage_ref']

