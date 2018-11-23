from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from users.models import Profile

from .models import Client, ClientWebsite
from .tasks import (invalidate_client_cache_task,
                    invalidate_mb_client_login_cache)


@receiver(pre_save, sender=Client, dispatch_uid='client_pre_save')
def client_pre_save(sender, **kwargs):
    """
    Client pre save signal
    """
    client = kwargs['instance']

    if not client.login:
        client.generate_login()

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
    tracker = client.tracker

    if tracker.has_changed('login') or tracker.has_changed('login_alias'):
        invalidate_mb_client_login_cache.delay(client_id=client.id)

    if client.installation == 'installed':
        invalidate_client_cache_task.delay(client_id=client.id)
    try:
        client.website
    except Client.website.RelatedObjectDoesNotExist:
        website = ClientWebsite()
        website.is_enabled = True
        website.client = client
        website.generate_url()
        website.save()
