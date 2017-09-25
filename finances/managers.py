import arrow
from django.apps import apps
from django.conf import settings

from billing.managers import LookupMixin


class OrderManager(LookupMixin):
    """"
    Order manager
    """
    lookup_search_fields = ('pk', 'client__name', 'client__email',
                            'client__login')

    def get_for_payment_notification(self):
        """
        Get orders for payment notification
        """
        now = arrow.utcnow()
        return self.filter(
            status__in=('new', 'processing'),
            expired_date__range=(now.datetime, now.shift(
                days=settings.MB_ORDER_PAYMENT_NOTIFY_DAYS).datetime))


class ServiceManager(LookupMixin):
    """"
    Service manager
    """

    lookup_search_fields = ('pk', 'title', 'description', 'type')

    def get_default(self, service_type):
        """
        Get default service
        """
        try:
            return self.get(
                type=service_type, is_enabled=True, is_default=True)
        except apps.get_model('finances', 'Service').DoesNotExist:
            return None
