import django_filters
from .models import FraisArrivage
from coordinates.models import Arrivage
from products.models import Employee


def arrivages(request):
    if request is None:
        return Arrivage.objects.none()

    enterprise = Employee.get_enterprise_of_current_user(request.user)
    return Arrivage.objects.filter(enterprise=enterprise)


class FraisArrivageFilter(django_filters.FilterSet):
    arrivage_ref = django_filters.ModelChoiceFilter(queryset=arrivages)

    class Meta:
        model = FraisArrivage
        fields = ['arrivage_ref']