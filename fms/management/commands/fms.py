import csv

from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand

from fms.models import Fms, Kpp


class Command(BaseCommand):
    help = 'Imports data from CSV files'

    def add_arguments(self, parser):
        parser.add_argument(
            'type', nargs='?', type=str, choices=('fms', 'kpp'))
        parser.add_argument('filepath', nargs='?', type=str)

    def handle(self, *args, **options):
        with open(options['filepath'], 'r', encoding='utf-8-sig') as f:
            r = csv.DictReader(f, delimiter=';', skipinitialspace=True)
            for row in r:
                entry = Fms() if options['type'] == 'fms' else Kpp()
                entry.internal_id = row['ID']
                entry.name = row['NAME']
                entry.code = row['CODE']
                if row['END_DATE']:
                    entry.end_date = row['END_DATE']
                try:
                    entry.full_clean()
                    entry.save()
                except ValidationError:
                    self.stdout.write(
                        self.style.ERROR('{} - ignore'.format(row['ID'])))
        self.stdout.write(self.style.SUCCESS('Successfully imported'))
