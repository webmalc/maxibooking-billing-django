"""
The clients signals module
"""
from corsheaders.signals import check_request_enabled
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from finances.models import ClientDiscount, Discount
from users.models import Profile

from .lib import cors
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
        user = Profile.objects.get_user_by_code(client.manager_code)
        client.manager = user


@receiver(post_save, sender=Client, dispatch_uid='client_post_save')
def client_post_save(sender, **kwargs):
    """
    Client post save signal
    """
    client = kwargs['instance']
    tracker = client.tracker

    if client.manager_code and not getattr(client, 'discount', None):
        discount = Discount.objects.get_by_code(client.manager_code)
        ClientDiscount.client_spanshot(discount, client)

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


def cors_allow_with_own_domains(sender, request, **kwargs):
    """
    Check if the CORS request is allowed
    """
    # TODO: cache the requests
    return cors.check_host(request.get_host())


check_request_enabled.connect(cors_allow_with_own_domains)
