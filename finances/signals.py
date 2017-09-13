import arrow
from django.conf import settings
from django.db.models.signals import m2m_changed, pre_save
from django.dispatch import receiver

from clients.models import ClientService

from .models import Order


@receiver(pre_save, sender=Order, dispatch_uid='order_pre_save')
def order_pre_save(sender, **kwargs):
    """
    Order pre save
    """

    order = kwargs['instance']
    if not order.expired_date:
        order.expired_date = arrow.utcnow().shift(
            days=+settings.MB_ORDER_EXPIRED_DAYS).datetime


# @receiver(
#     m2m_changed,
#     sender=Order.client_services.through,
#     dispatch_uid='order_m2m_changed')
def order_m2m_changed(sender, **kwargs):
    """
    Order m2m_changed
    """
    print(sender)


m2m_changed.connect(
    order_m2m_changed,
    # sender=Order.client_services.through,
    # sender=ClientService.orders.through,
    dispatch_uid='order_m2m_changed',
    weak=False)
