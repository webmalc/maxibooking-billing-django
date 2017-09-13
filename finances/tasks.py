import logging

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
    except order_model.DoesNotExist:
        logger.error('Order notify task failed {}.'.format(order_id))
    if order.status == 'new':
        mail_client(
            subject=_('New order created #') + str(order.id),
            template='emails/new_order.html',
            data={'order': order},
            client=order.client)
    logger.info('New order created {}.'.format(order))
