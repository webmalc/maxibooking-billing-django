from billing.celery import app
from billing.lib import mb

from .models import Client


@app.task
def install_client_task(client_id):
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
