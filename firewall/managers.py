from django.db import models

from .lib.decorators import cache_result
from .settings import FIREWALL_CACHE_KEY, FIREWALL_CACHE_TIMEOUT


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
