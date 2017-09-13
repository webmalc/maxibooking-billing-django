from ajax_select import register

from billing.lookup import BaseLookup

from .models import Client, ClientService


@register('order_client_services')
class ClientServiceLookup(BaseLookup):
    model = ClientService


@register('clients')
class ClientLookup(BaseLookup):
    model = Client
