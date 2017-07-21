from django.core.management.base import BaseCommand, CommandError

from finance.models import Currency, Converter

class Command(BaseCommand):
    help = 'Get currencies from webservice with Converter and load them (updating or creating) in database.'

    def handle(self, *args, **options):
        converter = Converter()
        converter.get_rates_webservice() # dump to the pickle file finance/rates.txt
        converter.get_all_currencies_webservice()   # dump to the pickle file finance/currencies.txt
        total = Currency.load_currencies() # Currency factory to create instances with the pickle files.
        self.stdout.write(self.style.SUCCESS('%s currencies loaded.' % total))







