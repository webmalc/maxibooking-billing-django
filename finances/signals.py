import logging

import arrow
from django.conf import settings
from django.db.models.signals import m2m_changed, post_save, pre_save
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _

from billing.lib.trans import auto_populate
from clients.tasks import mail_client_task

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

    if not order.price and order.id:
        order.price = order.calc_price()
    if not order.note and order.id:
        auto_populate(order, 'note', order.generate_note)


@receiver(post_save, sender=Order, dispatch_uid='order_post_save')
def order_post_save(sender, **kwargs):
    """
    Order post save
    """
    order = kwargs['instance']
    if not kwargs['created'] and order.tracker.has_changed('status') and \
       order.status == 'paid':
        mail_client_task.delay(
            subject=_('Your payment was successful'),
            template='emails/order_paid.html',
            data={'order_id': order.pk},
            client_id=order.client.id)

        logger = logging.getLogger('billing')
        logger.info('Order paid #{}. Payment system: {}'.format(
            order.pk, order.payment_system))

        order.client.check_status()

    if kwargs['created']:
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

    if not isinstance(order, Order) or order.status == 'corrupted':
        return None

    order.set_corrupted()

    is_changed = False
    if not order.note:
        auto_populate(order, 'note', order.generate_note)
        is_changed = True
    if not order.price:
        order.price = order.calc_price()
        is_changed = True
    if is_changed:
        order.save()
