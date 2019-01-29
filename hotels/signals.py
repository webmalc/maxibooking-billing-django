from django.db.models.signals import pre_save
from django.dispatch import receiver

from billing.lib.timezone import get_timezone
from hotels.models import City


@receiver(
    pre_save,
    sender=City,
    dispatch_uid='city_set_timezone_on_save',
)
def city_set_timezone_on_save(sender, **kwargs):
    """
    Set the city timezone on save
    """
    city = kwargs['instance']
    if not city.timezone:
        try:
            city.timezone = get_timezone(city=city)
        except ValueError:
            city.timezone = 'UTC'
