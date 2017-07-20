from billing.celery import app
from billing.lib import mb
from billing.lib.messengers.mailer import Mailer

from .models import Client


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

    client.installation = 'process'
    client.save()
    mb.install_client(client)

    return True


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
