from django.apps import apps
from django.db import models

from billing.exceptions import BaseException


class ClientServiceManager(models.Manager):
    """"
    ClientService manager
    """

    def make_trial(self, client):
        if client.status != 'not_confirmed':
            raise BaseException('client confirmed')
        if client.services.count():
            raise BaseException('client already has services')
        service_manager = apps.get_model('finances', 'Service').objects

        connection = service_manager.get_default('connection')
        if not connection:
            raise BaseException('default connection service not found')

        rooms = service_manager.get_default('rooms')
        if not rooms:
            raise BaseException('default rooms service not found')
