from django.core.management.base import BaseCommand, CommandError

from finance.models import Converter

class Command(BaseCommand):
    help = 'Download exchange rates.'

    def handle(self, *args, **options):
        converter = Converter()
        converter.get_rates_webservice()





