from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand
from tqdm import tqdm

from hotels.models import City, Country, Region


class Command(BaseCommand):
    help = 'Translate countries, regions, cities and add timezone to cities'

    def add_arguments(self, parser):
        parser.add_argument(
            '--timezone',
            action='store_true',
            dest='timezone',
            help='Set timezone to the cities',
        )

    def _process_model(self, model, timezone=False):
        self.stdout.write(
            self.style.SUCCESS('Process model: {}'.format(model)))
        errors = 0
        for obj in tqdm(model.objects.all()):
            if not obj.name_ru:
                name = obj.get_first_cyrilic_alternate_name()
                if name:
                    obj.name_ru = name
                    obj.save()
                else:
                    errors += 1
            if isinstance(obj, City) and timezone:
                obj.timezone = None
                try:
                    obj.save()
                except ValidationError as e:
                    print(str(e))
        if errors > 0:
            self.stdout.write(
                self.style.WARNING(
                    'Translations not found: {}'.format(errors)))

    def handle(self, *args, **options):
        for model in (Country, Region, City):
            self._process_model(model, options.get('timezone', False))
        self.stdout.write(self.style.SUCCESS('Successfully translated'))
