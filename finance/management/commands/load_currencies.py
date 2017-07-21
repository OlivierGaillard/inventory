from django.core.management.base import BaseCommand, CommandError

from finance.models import Currency

class Command(BaseCommand):
    help = 'Load currencies in database.'

    def handle(self, *args, **options):
        total = Currency.load_currencies()
        self.stdout.write(self.style.SUCCESS('%s currencies loaded.' % total))







