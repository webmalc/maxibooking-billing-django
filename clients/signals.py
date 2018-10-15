from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from users.models import Profile

from .models import Client
from .tasks import invalidate_client_cache_task


@receiver(pre_save, sender=Client, dispatch_uid='client_pre_save')
def client_pre_save(sender, **kwargs):
    """
    Client post save signal
    """
    client = kwargs['instance']

    if client.manager_code and not client.manager:
        try:
            profile = Profile.objects.get(code=client.manager_code)
            client.manager = profile.user
        except Profile.DoesNotExist:
            pass


@receiver(post_save, sender=Client, dispatch_uid='client_post_save')
def client_post_save(sender, **kwargs):
    """
    Client post save signal
    """
    client = kwargs['instance']

    if client.installation == 'installed':
        invalidate_client_cache_task.delay(client_id=client.id)
