from django.conf import settings


def get(param, default):
    """
    Get param from django settings
    """
    return getattr(settings, 'FIREWALL_ALLOW_BY_DEFAULT', default)


FIREWALL_ALLOW_BY_DEFAULT = get('FIREWALL_ALLOW_BY_DEFAULT', True)
