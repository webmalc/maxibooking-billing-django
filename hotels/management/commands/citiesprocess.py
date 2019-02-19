from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand
from tqdm import tqdm

from finances.lib.calc import get_currency_by_country
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
        for obj in tqdm(model.objects.all()):
            self._save_cyrilic_name(obj)
            self._save_country_currency(obj)
            if timezone:
                self._save_city_timezone(obj)

    def _save_cyrilic_name(self, obj):
        if not obj.name_ru:
            name = obj.get_first_cyrilic_alternate_name()
            if name:
                obj.name_ru = name
                obj.save()

    def _save_city_timezone(self, obj):
        if isinstance(obj, City):
            obj.timezone = None
            try:
                obj.save()
            except ValidationError as e:
                print(str(e))

    def _save_country_currency(self, obj):
        if isinstance(obj, Country) and not obj.currency:
            obj.currency = get_currency_by_country(obj)
            try:
                obj.save()
            except ValidationError as e:
                print(str(e))

    def handle(self, *args, **options):
        for model in (Country, Region, City):
            self._process_model(model, options.get('timezone', False))
        self.stdout.write(self.style.SUCCESS('Successfully processed'))
