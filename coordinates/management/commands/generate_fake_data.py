from django.core.management.base import BaseCommand
from faker import Factory, Faker
from coordinates.models import Contact, ContactPhone
from random import randint

class Command(BaseCommand):
    help = 'Create fake contacts and load them in database.'

    def handle(self, *args, **options):
        Contact.objects.all().delete()
        fake = Factory.create('fr_FR')
        n = 0
        for i in range(0,300):
            n += 1
            contact = Contact.objects.create(prenom=fake.first_name(), nom=fake.last_name(), email=fake.email())
            for i in range(0, randint(1,3)):
                ContactPhone.objects.create(contact=contact, phone_number=fake.phone_number(), phone_type=randint(1,3))
        self.stdout.write(self.style.SUCCESS('%s contacts created.' % n))

