from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ObjectDoesNotExist

from finance.models import Currency, Converter

class Command(BaseCommand):
    help = "Update currencies field 'used' in database."

    def add_arguments(self, parser):
        parser.add_argument('code', nargs='*')

        parser.add_argument(
            '--all_false',
            action='store_true',
            default=False,
            help='Set all currencies used to false',
        )

    def handle(self, *args, **options):
        if options['all_false']:
            total = 0
            for c in Currency.objects.all():
                Currency.objects.filter(pk=c.pk).update(used=False)
                total += 1
            print(total, ' currencies updated to used=False.')
        for code in options['code']:
            try:
                c = Currency.objects.get(currency_code=code)
                c.used=True
                c.save()
                print(code, ' used set to True')
            except ObjectDoesNotExist:
                print('Code %s was not found in table Currency.' % code)





