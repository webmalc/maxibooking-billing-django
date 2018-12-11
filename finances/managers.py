import arrow
from django.apps import apps
from django.conf import settings
from django.db import models

from billing.managers import LookupMixin


class SubscriptionManager(LookupMixin):
    """"
    The subscription manager
    """
    lookup_search_fields = ('id', '=order__pk', 'client__email',
                            'client__name', 'client__login')

    def get_active(self, client, pk=None):
        query = self.filter(client=client, status='enabled')
        if pk:
            query = query.exclude(pk=pk)
        return query


class OrderManager(LookupMixin):
    """"
    Order manager
    """
    lookup_search_fields = ('id', 'client__name', 'client__email',
                            'client__login')

    def get_for_payment_system(self, pk):
        """
        Get order for payment systems
        """
        try:
            return self.select_related('client', 'client__ru').get(
                pk=pk, status='new', client__phone__isnull=False)
        except self.model.DoesNotExist:
            return None

    def get_for_payment_notification(self):
        """
        Get orders for payment notification
        """
        now = arrow.utcnow()
        return self.filter(
            status__in=('new', 'processing'),
            expired_date__range=(
                now.datetime,
                now.shift(days=settings.MB_ORDER_PAYMENT_NOTIFY_DAYS).datetime
            )).exclude(client__status__in=('disabled', 'archived'))

    def get_expired(self, exclude_client_statuses=('disabled', 'archived')):
        """
        Get expired orders
        """
        now = arrow.utcnow()
        return self.filter(
            status__in=('new', 'processing'),
            expired_date__lte=now.datetime).exclude(
                client__status__in=exclude_client_statuses)


class PriceManager(models.Manager):
    def filter_by_country(self, country, service):
        """
        Get prices for country
        """
        base_query = self.filter(service=service, is_enabled=True)
        query = base_query.filter(country=country)
        if not query.count():
            query = base_query.filter(country__isnull=True)
        return query


class ServiceManager(LookupMixin):
    """"
    Service manager
    """

    lookup_search_fields = ('id', 'title', 'description', 'type')

    def get_by_period(self, service_type, period, period_units='month'):
        """
        Get service by duration
        """
        try:
            return self.get(
                type=service_type,
                is_enabled=True,
                period=period,
                period_units=period_units,
            )
        except apps.get_model('finances', 'Service').DoesNotExist:
            return None

    def get_all_periods(self, service_type, period_units='month'):
        """
        Get all services periods
        """
        return self.filter(
            type=service_type,
            is_enabled=True,
            period_units=period_units,
        ).order_by('period')

    def get_default(self, service_type):
        """
        Get default service
        """
        try:
            return self.get(
                type=service_type, is_enabled=True, is_default=True)
        except apps.get_model('finances', 'Service').DoesNotExist:
            return None
