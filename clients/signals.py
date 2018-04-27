from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Client
from .tasks import invalidate_client_cache_task


@receiver(post_save, sender=Client, dispatch_uid='client_post_save')
def order_post_save(sender, **kwargs):
    """
    Client post save
    """
    client = kwargs['instance']
    invalidate_client_cache_task.delay(client_id=client.id)
