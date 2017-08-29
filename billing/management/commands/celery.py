import shlex
import subprocess

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import autoreload


def celery(mode):
    """
    Restarts celery

    Keyword arguments:
    mode - worker or beat
    """
    commands = [
        'pkill -9 celery',
        'celery {} -A {} --loglevel {}'.format(mode, settings.CELERY_APP,
                                               settings.CELERY_LOGLEVEL),
    ]
    for cmd in commands:
        subprocess.call(shlex.split(cmd))


class Command(BaseCommand):
    """
    Celery with autoreload
    """

    def add_arguments(self, parser):
        parser.add_argument(
            'mode', nargs='?', default='worker', choices=['worker', 'beat'])

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('Starting celery worker with autoreload'))
        autoreload.main(celery(options['mode']))
