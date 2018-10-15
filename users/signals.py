from django.db.models.signals import pre_save
from django.dispatch import receiver

from .models import Profile


@receiver(pre_save, sender=Profile, dispatch_uid='profile_post_save')
def order_post_save(sender, **kwargs):
    """
    User`s profile post save
    """
    profile = kwargs['instance']

    def generate(profile):
        profile.generate_code()
        if Profile.objects.filter(code=profile.code).count():
            generate(profile)
        return profile

    if not profile.code:
        generate(profile)
