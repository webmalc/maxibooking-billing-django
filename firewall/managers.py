from django.db import models


class RuleManager(models.Manager):
    """"
    Rule manager
    """

    def fetch(self):
        """
        Get all enabled rules
        """
        return self.filter(is_enabled=True).prefetch_related('groups')
