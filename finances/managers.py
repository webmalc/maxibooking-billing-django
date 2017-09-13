from django.apps import apps

from billing.managers import LookupMixin


class OrderManager(LookupMixin):
    """"
    Order manager
    """
    lookup_search_fields = ('pk', 'client__name', 'client__email',
                            'client__login')


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
