import arrow
from django.apps import apps
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db.models import Case, Count, IntegerField, Q, Sum, When

from billing.exceptions import BaseException
from billing.managers import DepartmentMixin, LookupMixin
from hotels.models import Room


class ClientWebsiteManager(LookupMixin):
    """
    The ClientWebsite manager
    """

    lookup_search_fields = ('id', 'client__login', 'client__email',
                            'client__name', 'url')

    def check_by_own_domain(self, host: str):
        """
        Check if there is a client website with its own domain
        with the host provided
        """
        return self.filter(
            url__icontains=host, is_enabled=True,
            own_domain_name=True).count() > 0


class CompanyManager(LookupMixin, DepartmentMixin):
    """"
    Company manager
    """
    lookup_search_fields = ('id', 'client__login', 'client__email',
                            'client__name', 'name', 'ru__boss_lastname',
                            'ru__ogrn', 'ru__inn', 'ru__kpp', 'account_number',
                            'ru__bik', 'world__swift')

    def get_for_bill(self, client):
        return self.filter(client=client).exclude(ru__isnull=True).first()


class ServiceCategoryGroup(object):
    """
    Container for grouped client services
    """

    def __init__(self, category, price=0, quantity=0):
        self.client_services = set()
        self.category = category
        self.price = price
        self.quantity = quantity

    def add_client_services(self, *args):
        """
        Add client service to group
        """
        for client_service in args:
            if client_service.service.category != self.category:
                raise ValueError('Invalid client_service category')
            self.client_services.add(client_service)
            try:
                self.price += client_service.price
            except TypeError:
                self.price = -1

            self.quantity += client_service.group_quantity

    @property
    def begin(self):
        return list(self.client_services)[0].begin

    @property
    def end(self):
        return list(self.client_services)[0].end


class ClientManager(LookupMixin, DepartmentMixin):
    """"
    Client manager
    """
    lookup_search_fields = ('pk', 'login', 'email', 'phone', 'name',
                            'country__name')

    def get_by_login(self, login: str, exclude_pk: int = None, query=None):
        """
        Get clients by their login or alias
        """
        if not query:
            query = self.all()

        query = self.filter(Q(login=login) | Q(login_alias=login))
        if exclude_pk:
            query = query.exclude(pk=exclude_pk)
        return query

    def get_for_greeting(self,
                         days=settings.MB_CLIENT_GREETING_EMAIL_DAYS,
                         query=None):
        query = self.get_trial(query)
        begin = arrow.utcnow().shift(days=-days).floor('day').datetime
        end = arrow.utcnow().shift(days=-(days - 1)).floor('day').datetime
        return query.filter(created__range=(begin, end))

    def get_trial(self, query=None):
        """
        The method for getting the trial clients
        """
        query = query if query else self.all()

        query = query.annotate()

        return query.filter(
            status='active', ).prefetch_related('orders').annotate(
                orders_count=Count(
                    Case(
                        When(orders__status='paid', then=1),
                        output_field=IntegerField()))).filter(orders_count=0)

    def get_disabled(self,
                     days=settings.MB_CLIENT_DISABLED_FIRST_EMAIL_DAYS,
                     query=None):
        """
        The method for getting the disabled clients
        """
        query = query if query else self.all()
        begin = arrow.utcnow().shift(days=-days).floor('day').datetime
        end = arrow.utcnow().shift(days=-(days - 1)).floor('day').datetime

        return query.filter(
            status='disabled',
            disabled_at__range=(begin, end)).exclude(disabled_at__isnull=True)

    def get_for_archivation(self, query=None):
        """
        Get clients for archivation
        """
        query = query if query else self.all()
        return query.filter(
            status='disabled',
            disabled_at__lte=arrow.utcnow().shift(
                months=-settings.MB_CLIENT_ARCHIVE_MONTHS).datetime).exclude(
                    disabled_at__isnull=True)

    def count_rooms(self, client):
        """
        Count client service rooms
        """
        now = arrow.utcnow().datetime
        rooms = client.services.filter(
            service__type='rooms',
            begin__lte=now,
            status='active',
            # is_enabled=True,
        ).aggregate(Sum('quantity'))['quantity__sum']

        return int(rooms or 0)

    def get_by_orders(self, paid, query=None):
        """
        Get clients by orders
        """
        query = query if query else self.all()
        query = query.annotate(
            orders_count=Count(
                Case(
                    When(orders__status='paid', then=1),
                    output_field=IntegerField())))
        if paid:
            query = query.filter(orders_count__gte=1)
        else:
            query = query.filter(orders_count=0)
        return query


class ClientServiceManager(LookupMixin, DepartmentMixin):
    """"
    ClientService manager
    """
    lookup_search_fields = ('pk', 'service__title', 'client__name',
                            'client__email', 'client__login')

    def client_tariff_update(self, client, rooms, period):
        """
        Update clients rooms services
        """
        service_manager = apps.get_model('finances', 'Service').objects

        rooms_service = service_manager.get_by_period('rooms', period)
        if not rooms_service:
            raise BaseException('rooms service not found')

        client.services.filter(status='next').update(
            status='archive',
            is_enabled=False,
        )
        if rooms > 0:
            self._create_service(rooms_service, client, rooms, 'next', True)

    def get_prev(self, client_service, service_type=None):
        if not service_type:
            service_type = client_service.service.type
        if client_service.status == 'next':
            return self.filter(
                status='active',
                client=client_service.client,
                service__type='rooms').first()
        try:
            return self.get(
                # is_enabled=True,
                status='active',
                client=client_service.client,
                service__type=service_type)
        except apps.get_model('clients', 'ClientService').DoesNotExist:
            return None

    def get_services_by_category(self, query):
        """
        Get query services grouped by category
        """
        grouped_services = {}
        for e in query:
            cat = e.service.category
            if cat.id not in grouped_services:
                grouped_services[cat.id] = ServiceCategoryGroup(cat)
            group = grouped_services[cat.id]
            group.add_client_services(e)
        return list(grouped_services.values())

    def get_client_services_by_category(self, client, next=False):
        """
        Get client services grouped by category
        """
        statuses = ('active', 'processing')
        if next:
            statuses = ('next', )
        entries = client.services.filter(
            # is_enabled=True,
            status__in=statuses,
            service__type__in=('rooms', )).select_related(
                'service', 'client', 'service__category')
        return self.get_services_by_category(entries)

    def get_order_services_by_category(self, order):
        """
        Get order services grouped by category
        """

        entries = self.filter(
            orders__pk=getattr(order, 'pk', order)).select_related(
                'service', 'client', 'service__category')
        return self.get_services_by_category(entries)

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

    def deactivate(self, client, service_type=None, exclude_pk=None):
        """
        Deactivate client services by params
        """
        query = self.filter(client=client)

        if service_type:
            query = query.filter(service__type=service_type)
        if exclude_pk:
            query = query.exclude(pk=exclude_pk)
        return query.update(status='archive')

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
        return self.filter(
            Q(end__lt=end, status='active') | Q(
                begin__lt=end,
                status='next',
                is_paid=False,
            ),
            is_enabled=True,
        ).exclude(
            service__period=0,
            client__status='archived',
        ).select_related('client').prefetch_related('orders').order_by(
            'client', '-created')

    def find_for_activation(self):
        """
        Find client sevices for activation
        """
        return self.filter(
            begin__lte=arrow.utcnow().datetime,
            status='next',
            is_paid=True,
            is_enabled=True,
        ).select_related('client').order_by('client', '-created')

    def make_trial(self, client):
        """
        Create client trial services
        """
        if client.services.count():
            raise BaseException('client already has services')
        service_manager = apps.get_model('finances', 'Service').objects

        rooms = service_manager.get_default('rooms')
        if not rooms:
            raise BaseException('default rooms service not found')

        client.trial_activated = True
        client.save()
        rooms_max = Room.objects.count_rooms(client)
        if rooms_max > 0:
            self._create_service(rooms, client, rooms_max, trial=True)

    def _create_service(
            self,
            service,
            client,
            quantity,
            status='active',
            connection=False,
            trial=False,
    ):
        """
        Create client service
        """
        client_service_model = apps.get_model('clients', 'ClientService')

        client_service = client_service_model()
        client_service.service = service
        client_service.client = client
        client_service.quantity = quantity
        client_service.status = status
        if connection:
            client_service.begin = client_service.get_default_begin()
        if trial:
            client_service.end = arrow.get(client_service.begin).shift(
                days=settings.MB_TRIAL_DAYS).datetime
        try:
            client_service.full_clean()
            client_service.save()
        except ValidationError as e:
            raise BaseException(
                'invalid default service: {}. Error: {}'.format(service, e))
