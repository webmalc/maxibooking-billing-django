import logging

import arrow
from django.apps import apps
from django.utils.translation import ugettext_lazy as _

from billing.celery import app
from billing.lib.messengers.mailer import mail_client


@app.task
def order_notify_task(order_id):
    """
    Order client notification
    """
    logger = logging.getLogger('billing')
    order_model = apps.get_model('finances', 'Order')
    try:
        order = order_model.objects.get(pk=order_id)
        if order.status == 'new':
            mail_client(
                subject=_('New order created'),
                template='emails/new_order.html',
                data={'order': order},
                client=order.client)
        logger.info('New order created {}.'.format(order))
    except order_model.DoesNotExist:
        logger.error('Order notify task failed {}.'.format(order_id))


@app.task
def orders_payment_notify():
    """
    Order payments notification
    """
    orders = apps.get_model('finances',
                            'Order').objects.get_for_payment_notification()
    for order in orders:
        mail_client(
            subject=_('Order will expire soon').format(order.pk),
            template='emails/order_payment_notification.html',
            data={'order': order},
            client=order.client)


@app.task
def orders_clients_disable():
    """
    Expired orders clients disable
    """
    orders = apps.get_model('finances', 'Order').objects.get_expired()
    for order in orders:
        client = order.client
        client.status = 'disabled'
        client.disabled_at = arrow.utcnow().datetime
        client.save()
        logger = logging.getLogger('billing')
        logger.info('Client disabled {}.'.format(client))

        mail_client(
            subject=_('Your account is disabled'),
            template='emails/order_client_disabled.html',
            data={'url': order.client.url},
            client=order.client)
