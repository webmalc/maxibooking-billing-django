from django.core.management.base import BaseCommand
from tqdm import tqdm

from hotels.models import City, Country, Region


class Command(BaseCommand):
    help = 'Translate countries, regions, cities'

    def _process_model(self, model):
        self.stdout.write(
            self.style.SUCCESS('Process model: {}'.format(model)))
        errors = 0
        for obj in tqdm(model.objects.all()):
            name = obj.get_first_cyrilic_alternate_name()
            if name:
                obj.name_ru = name
                obj.save()
            else:
                errors += 1
        if errors > 0:
            self.stdout.write(
                self.style.WARNING('Translations not found: {}'.format(
                    errors)))

    def handle(self, *args, **options):
        for model in (Country, Region, City):
            self._process_model(model)
        self.stdout.write(self.style.SUCCESS('Successfully translated'))
