from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import ClientService


@receiver(
    post_save, sender=ClientService, dispatch_uid='client_service_post_save')
def client_service_post_save(sender, **kwargs):
    """
    ClientService post save
    """
    client_service = kwargs['instance']
    client_service.client.restrictions_update()
