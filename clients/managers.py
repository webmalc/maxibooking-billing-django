import arrow
from django.apps import apps
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db.models import Sum

from billing.exceptions import BaseException
from billing.managers import LookupMixin
from hotels.models import Room


class ClientManager(LookupMixin):
    """"
    Client manager
    """
    lookup_search_fields = ('pk', 'login', 'email', 'phone', 'name',
                            'country__name')

    def get_for_archivation(self, query=None):
        """
        Get clients for archivation
        """
        return self.filter(
            status='disabled',
            disabled_at__lte=arrow.utcnow().shift(
                months=-settings.MB_CLIENT_ARCHIVE_MONTHS).datetime).exclude(
                    disabled_at__isnull=True)

    def count_rooms(self, client):
        """
        Count client service rooms
        """
        rooms = client.services.filter(
            service__type='rooms',
            begin__lte=arrow.utcnow().datetime,
            is_enabled=True).aggregate(Sum('quantity'))['quantity__sum']

        default_rooms = client.services.filter(
            service__type='connection',
            begin__lte=arrow.utcnow().datetime,
            is_enabled=True).aggregate(
                Sum('service__default_rooms'))['service__default_rooms__sum']

        return int(rooms or 0) + int(default_rooms or 0)


class ClientServiceManager(LookupMixin):
    """"
    ClientService manager
    """
    lookup_search_fields = ('pk', 'service__title', 'client__name',
                            'client__email', 'client__login')

    def get_prev(self, client_service):
        try:
            return self.get(
                is_enabled=True,
                client=client_service.client,
                service__type=client_service.service.type)
        except apps.get_model('clients', 'ClientService').DoesNotExist:
            return None

    def disable(self, client, service_type=None, exclude_pk=None):
        """
        Disable client services by params
        """
        query = self.filter(client=client, is_enabled=True)

        if service_type:
            query = query.filter(service__type=service_type)
        if exclude_pk:
            query = query.exclude(pk=exclude_pk)
        return query.update(is_enabled=False)

    def total(self, query=None):
        """
        Get total price
        """
        query = query if query else self.all()
        total = 0
        for s in query.filter(is_enabled=True):
            total += s.price
        return total if total else 0

    def find_ended(self):
        """
        Find ended client services
        """
        end = arrow.utcnow().shift(
            days=+settings.MB_ORDER_BEFORE_DAYS).datetime
        return self.filter(end__lt=end, status='active', is_enabled=True).\
            exclude(service__period=0, client__status='archived').\
            select_related('client').order_by('client', '-created')

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
        rooms_max = Room.objects.count_rooms(client)
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
