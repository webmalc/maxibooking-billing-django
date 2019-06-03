import logging
from itertools import groupby

from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from billing.celery import app
from billing.lib import mb
from billing.lib.lang import select_locale
from billing.lib.messengers.mailer import mail_client, mail_managers
from finances.models import Order

from .models import Client, ClientService


@app.task
def invalidate_client_cache_task(client_id):
    """
    Client invalidation task
    """
    try:
        client = Client.objects.get(pk=client_id)
    except Client.DoesNotExist:
        return False
    mb.client_cache_invalidate(client)

    return True


@app.task
def install_client_task(client_id):
    """
    Client installation task
    """
    try:
        client = Client.objects.get(pk=client_id)
    except Client.DoesNotExist:
        return False

    if client.installation == 'installed':
        return False

    if mb.client_install(client):
        client.installation = 'process'
        client.save()
        return True

    return False


@app.task
def mail_managers_task(subject, data, template=None):
    if template:
        mail_managers(subject, data, template)
    else:
        mail_managers(subject, data)


@app.task
def mail_client_task(
        subject,
        template,
        data,
        client_id=None,
        email=None,
        lang=None,
):
    """
    Mail to site client or email
    """
    if email:
        mail_client(
            subject=subject,
            template=template,
            data=data,
            email=email,
            lang=lang,
        )
        return True

    if client_id:
        try:
            client = Client.objects.get(pk=client_id)
            mail_client(subject=subject,
                        template=template,
                        data=data,
                        client=client)
            return True
        except Client.DoesNotExist:
            return False


@app.task
def client_greeting_email(days=settings.MB_CLIENT_GREETING_EMAIL_DAYS):
    """
    The task for sending welcome emails to trial clients
    """
    clients = Client.objects.get_for_greeting(days)
    for client in clients:
        with select_locale(client):
            mail_client(subject=_('How is your Sales?'),
                        template='emails/client_welcome.html',
                        data={
                            'client': client,
                        },
                        client=client)


@app.task
def client_disabled_email(days=settings.MB_CLIENT_DISABLED_FIRST_EMAIL_DAYS):
    """
    The task for sending emails to disabled clients
    """
    clients = Client.objects.get_disabled(days)
    for client in clients:
        with select_locale(client):
            mail_client(subject=_('we miss You!'),
                        template='emails/client_disabled.html',
                        data={
                            'order':
                            client.orders.get_expired(('archived', )).first(),
                            'client':
                            client,
                        },
                        client=client)


@app.task
def invalidate_mb_client_login_cache(client_id):
    """
    Invalidate client login cache on the remote Maxibooking server
    """
    try:
        client = Client.objects.get(pk=client_id)
    except Client.DoesNotExist:
        return False
    mb.client_login_cache_invalidate(client)

    return True


@app.task
def client_services_activation():
    """
    Client services periodical activation
    """
    client_services = ClientService.objects.find_for_activation()
    for client_service in client_services:
        logging.getLogger('billing').info(
            'Activation client service {}'.format(client_service))
        client_service.status = 'active'
        client_service.save()
        client_service.client.restrictions_update()


@app.task
def client_services_update():
    """
    Client services periodical update
    """
    client_services = [
        s for s in ClientService.objects.find_ended()
        if not s.orders.filter(status__in=('new', 'processing')).count()
    ]
    grouped_services = [
        list(r) for k, r in groupby(client_services, lambda i: i.client.id)
    ]
    for group in grouped_services:
        order = Order()
        order.client = group[0].client
        order.save()
        for client_service in group:
            logging.getLogger('billing').info(
                'Generating order for client service {}'.format(
                    client_service))
            if client_service.status != 'next':
                client_service.end = client_service.service.get_default_end(
                    client_service.end)
            # client_service.status = 'processing'
            client_service.is_paid = False
            client_service.price = None
            client_service.save()
            order.client_services.add(client_service)
        order.price = None
        order.save()


@app.task
def client_archivation():
    """
    Client archivation
    """
    clients = Client.objects.get_for_archivation()
    for client in clients:
        mb.client_archive(client)
