from ..models import Order
from .types import Bill, Rbk, Stripe


def list(order=None):
    """
    Get payment systems list
    """
    if order and not isinstance(order, Order):
        order = Order.objects.get_for_payment_system(order)
    types = {}
    types['stripe'] = Stripe(order)
    types['rbk'] = Rbk(order)
    types['bill'] = Bill(order)
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


def get(id, order=None):
    """
    Get payment system by name
    """
    try:
        return list(order)[id]
    except KeyError:
        return None