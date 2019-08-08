from django.core.cache import cache
from django.db.models.signals import post_save
from django.dispatch import receiver
from djmoney.contrib.exchange.models import Rate

from clients.tasks import mail_managers_task

from .models import CachedModel, CheckedModel


@receiver(post_save, dispatch_uid='cached_model_post_save')
def cached_model_post_save(sender, **kwargs):
    """
    Cached model post save
    """
    models = (CachedModel, Rate)
    for model in models:
        if isinstance(kwargs['instance'], model):
            cache.clear()


@receiver(post_save, dispatch_uid='checked_model_post_save')
def checked_model_post_save(sender, **kwargs):
    """
    Cached model post save
    """
    instance = kwargs['instance']
    if isinstance(instance, CheckedModel) and not instance.is_checked:

        mail_managers_task.delay(
            subject='New object for moderation',
            data={
                'text':
                'New object for moderation: {}, id - {}, info - {}'.format(
                    instance, instance.pk, instance.__repr__())
            })
