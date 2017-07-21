from django.core.management.base import BaseCommand, CommandError

from finance.models import Currency, Converter

class Command(BaseCommand):
    help = 'Update currencies rate in database using web service and then pickle file.'

    def handle(self, *args, **options):
        converter = Converter()
        converter.get_rates_webservice()
        li = Currency.objects.all()
        for currency in li: currency.save()





