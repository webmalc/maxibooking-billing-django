import logging
from itertools import groupby

from billing.celery import app
from billing.lib import mb
from billing.lib.messengers.mailer import mail_client
from finances.models import Order

from .models import Client, ClientService


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

    if mb.install_client(client):
        client.installation = 'process'
        client.save()
        return True

    return False


@app.task
def mail_client_task(subject, template, data, client_id=None, email=None):
    """
    Mail to site client or email
    """
    if email:
        mail_client(subject=subject, template=template, data=data, email=email)
        return True

    if client_id:
        try:
            client = Client.objects.get(pk=client_id)
            mail_client(
                subject=subject, template=template, data=data, client=client)
            return True
        except Client.DoesNotExist:
            return False


@app.task
def client_services_update():
    """
    Client services periodical update
    """
    client_services = list(ClientService.objects.find_ended())

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
            client_service.end = client_service.service.get_default_end(
                client_service.end)
            client_service.status = 'processing'
            client_service.price = None
            client_service.save()
            order.client_services.add(client_service)
        order.save()
