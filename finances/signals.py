import arrow
from django.conf import settings
from django.db.models.signals import m2m_changed, post_save, pre_save
from django.dispatch import receiver

from .models import Order
from .tasks import order_notify_task


@receiver(pre_save, sender=Order, dispatch_uid='order_pre_save')
def order_pre_save(sender, **kwargs):
    """
    Order pre save
    """

    order = kwargs['instance']
    if not order.expired_date:
        order.expired_date = arrow.utcnow().shift(
            days=+settings.MB_ORDER_EXPIRED_DAYS).datetime


@receiver(post_save, sender=Order, dispatch_uid='order_post_save')
def order_post_save(sender, **kwargs):
    """
    Order post save
    """
    if kwargs['created']:
        order = kwargs['instance']
        order_notify_task.apply_async((order.id, ), countdown=1)


@receiver(
    m2m_changed,
    sender=Order.client_services.through,
    dispatch_uid='order_m2m_changed')
def order_m2m_changed(sender, **kwargs):
    """
    Order m2m_changed
    """
    if kwargs['action'] not in ('post_add', 'post_remove', 'post_clear'):
        return None
    order = kwargs['instance']
    is_changed = False
    if not order.note:
        order.note = order.generate_note()
        is_changed = True
    if not order.price:
        order.price = order.calc_price()
        is_changed = True
    if is_changed:
        order.save()
