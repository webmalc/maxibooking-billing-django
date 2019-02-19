import logging

import arrow
from django.apps import apps
from django.utils.translation import ugettext_lazy as _

from billing.celery import app
from billing.lib.lang import select_locale
from billing.lib.messengers.mailer import mail_client

from .lib.rates import update_exchange_rates


@app.task
def update_exchange_rates_task():
    """
    Update the exchange rates from the remote source
    """
    update_exchange_rates()


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
            greetings_new = ''
            client = order.client
            expired = order.expired_date
            # delta = arrow.get(expired) - arrow.now()
            with select_locale(client):
                if client.is_trial:
                    greetings_new = '<p>{}</p>'.format(
                        _('We are glad to see you among our clients!'))
                mail_client(
                    subject=_('New Invoice created'),
                    template='emails/new_order.html',
                    data={
                        'order': order,
                        'client': client,
                        'greetings_new': greetings_new,
                        'expired': expired,
                        'days': 3
                    },
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
        greetings_new = ''
        client = order.client
        with select_locale(client):
            if client.is_trial:
                greetings_new = '<p>{}</p>'.format(
                    _('We are glad to see you among our clients!'))

            mail_client(
                subject=_(
                    'Invoice is due - don’t forget to extend your access! '),
                template='emails/order_payment_notification.html',
                data={
                    'order': order,
                    'client': client,
                    'greetings_new': greetings_new
                },
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
            subject=_('Oh No! Your Account has been suspended'),
            template='emails/order_client_disabled.html',
            data={
                'url': order.client.url,
                'name': client.name,
                'order': order,
                'created': order.created.strftime('%d.%m.%Y')
            },
            client=order.client)
