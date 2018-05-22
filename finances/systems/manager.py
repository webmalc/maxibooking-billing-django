from importlib import import_module

from django.conf import settings

from ..models import Order


def systems_list(order=None, request=None, load=True):
    """
    Get payment systems list
    """
    if order and not isinstance(order, Order):
        order = Order.objects.get_for_payment_system(order)
    types = {}
    for s in settings.PAYMENT_SYSTEMS:
        s_class = getattr(import_module('finances.systems.models'), s.title())
        types[s] = s_class(order, request=request, load=load)
    if order:
        country = order.client.country.tld
        result = {}
        for k, v in types.items():
            if len(v.countries) and country not in v.countries:
                continue
            if len(v.countries_excluded) and country in v.countries_excluded:
                continue
            result[k] = v
    else:
        result = types
    return result


def get(id, order=None, request=None, load=True):
    """
    Get payment system by name
    """
    try:
        return systems_list(order, request=request, load=load)[id]
    except KeyError:
        return None
