from django.core.management.base import BaseCommand, CommandError

from finance.models import Currency

class Command(BaseCommand):
    help = 'Update currencies in database.'

    def handle(self, *args, **options):
        li = Currency.objects.all()
        for currency in li: currency.save()





