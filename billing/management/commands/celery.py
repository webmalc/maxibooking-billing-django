import shlex
import subprocess

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import autoreload


def restart_celery():
    cmd = 'pkill -9 celery'
    subprocess.call(shlex.split(cmd))
    cmd = 'celery worker -A {} --concurrency=4 --loglevel debug'.format(
        settings.CELERY_APP, settings.CELERY_LOGLEVEL)
    subprocess.call(shlex.split(cmd))


class Command(BaseCommand):
    """
    Celery with autoreload
    """

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('Starting celery worker with autoreload'))
        autoreload.main(restart_celery)
