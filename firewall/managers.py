# -*- coding: utf-8 -*-
"""
Django firewall manager classes
"""
from django.db import models

from .lib.decorators import cache_result
from .settings import FIREWALL_CACHE_KEY, FIREWALL_CACHE_TIMEOUT


class IpRangeManager(models.Manager):
    """"
    IpRange manager
    """

    def find_by_ip(self, start_ip, end_ip, exclude_pk=None):
        """
        Find range by ip
        """
        query = self.filter(start_ip=start_ip, end_ip=end_ip, is_enabled=True)
        if exclude_pk:
            query = query.exclude(pk=exclude_pk)
        return query


class RuleManager(models.Manager):
    """"
    Rule manager
    """

    @cache_result(FIREWALL_CACHE_KEY, FIREWALL_CACHE_TIMEOUT)
    def fetch(self):
        """
        Get all enabled rules
        """
        return self.filter(is_enabled=True).prefetch_related('groups')
