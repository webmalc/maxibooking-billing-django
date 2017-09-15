import arrow
from django.apps import apps
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from billing.exceptions import BaseException
from billing.managers import LookupMixin
from hotels.models import Property


class ClientManager(LookupMixin):
    """"
    Client manager
    """
    lookup_search_fields = ('pk', 'login', 'email', 'phone', 'name',
                            'country__name')


class ClientServiceManager(LookupMixin):
    """"
    ClientService manager
    """
    lookup_search_fields = ('pk', 'service__title', 'client__name',
                            'client__email', 'client__login')

    def total(self, query=None):
        """
        Get total price
        """
        query = query if query else self.all()
        total = query.filter(is_enabled=True).aggregate(
            total=models.Sum('price'))['total']
        return total if total else 0

    def find_ended(self):
        """
        Find ended client services
        """
        end = arrow.utcnow().shift(
            days=+settings.MB_ORDER_BEFORE_DAYS).datetime
        return self.filter(end__lt=end, status='active', is_enabled=True).\
            exclude(service__period=0).select_related('client').\
            order_by('client', '-created')

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
        rooms_max = Property.objects.count_rooms(client)
        self._make_trial_service(rooms, client, rooms_max)

    def _make_trial_service(self, service, client, quantity):
        """
        Create client service
        """
        client_service_model = apps.get_model('clients', 'ClientService')
        client_service = client_service_model()
        client_service.service = service
        client_service.client = client
        client_service.quantity = quantity
        client_service.status = 'active'
        try:
            client_service.full_clean()
            client_service.save()
        except ValidationError as e:
            raise BaseException('invalid default service: {}'.format(service))
