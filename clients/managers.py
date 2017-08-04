from django.apps import apps
from django.core.exceptions import ValidationError
from django.db import models

from billing.exceptions import BaseException


class ClientServiceManager(models.Manager):
    """"
    ClientService manager
    """

    def make_trial(self, client):
        """
        Create client trial services
        """
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

        self._make_trial_service(connection, client, 1)
        # TODO: count client rooms
        self._make_trial_service(rooms, client, 20)

    def _make_trial_service(self, service, client, quantity):
        """
        Create client service
        """
        client_service_model = apps.get_model('clients', 'ClientService')
        connection_service = client_service_model()
        connection_service.service = service
        connection_service.client = client
        connection_service.quantity = quantity
        try:
            connection_service.full_clean()
            connection_service.save()
        except ValidationError as e:
            raise BaseException('invalid default service: {}'.format(service))
