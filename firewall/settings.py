# -*- coding: utf-8 -*-
"""
Django firewall settings
"""
from django.conf import settings


def get(param, default):
    """
    Get param from django settings
    """
    return getattr(settings, param, default)


FIREWALL_ALLOW_BY_DEFAULT = get('FIREWALL_ALLOW_BY_DEFAULT', True)
FIREWALL_CACHE_TIMEOUT = get('FIREWALL_CACHE_TIMEOUT', 60 * 60 * 24)
FIREWALL_CACHE_KEY = get('FIREWALL_CACHE_KEY', 'firewall_rules')
FIREWALL_IPWARE_PROXY_COUNT = get('FIREWALL_IPWARE_PROXY_COUNT', None)
FIREWALL_LOGGING_HANDLER = get('FIREWALL_LOGGING_HANDLER', 'firewall')
FIREWALL_IPRANGES_ADMIN_MAX = get('FIREWALL_IPRANGES_ADMIN_MAX', 30)
