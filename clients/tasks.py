import logging

from billing.celery import app
from billing.lib import mb
from billing.lib.messengers.mailer import Mailer

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
        Mailer.mail_client(
            subject=subject, template=template, data=data, email=email)
        return True

    if client_id:
        try:
            client = Client.objects.get(pk=client_id)
            Mailer.mail_client(
                subject=subject, template=template, data=data, client=client)
            return True
        except Client.DoesNotExist:
            return False


@app.task
def client_services_update():
    """
    Client services periodical update
    """
    client_services = ClientService.objects.find_ended()
    for client_service in client_services:
        logging.getLogger('billing').info(
            'Generating order for client service {}'.format(client_service))
        client_service.end = client_service.service.get_default_end(
            client_service.end)
        client_service.status = 'processing'
        client_service.price = None
        client_service.save()

        # TODO: order create
