from ajax_select import register

from billing.lookup import BaseLookup

from .models import Order, Service


@register('orders')
class OrderLookup(BaseLookup):
    model = Order


@register('services')
class ServiceLookup(BaseLookup):
    model = Service
