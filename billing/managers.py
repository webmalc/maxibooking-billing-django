from abc import ABCMeta, abstractproperty
from functools import reduce

import arrow
from django.db import models
from django.db.models import Q


class LookupMixin(models.Manager, metaclass=ABCMeta):
    """
    LookupMixin
    """

    @abstractproperty
    def lookup_search_fields(self):
        return ('pk', )

    def lookup(self, q, request):
        """
        Base lookup query
        """

        return self.filter(
            reduce(lambda x, f: x | Q(**{'%s__icontains' % f: q}),
                   self.lookup_search_fields, Q()))[:100]


class DictManager(models.Manager):
    """
    Default manager for DictMixin
    """

    def filter_is_enabled(self):
        return self.filter(is_enabled=True)


class CommentsManager(models.Manager):
    """
    Comments manager
    """

    def get_uncompleted(self):
        """
        Get uncompleted actions
        """
        begin = arrow.utcnow().shift(days=-2).datetime
        end = arrow.utcnow().shift(hours=-2).datetime

        return self.filter(
            type='action',
            date__range=(begin, end),
        ).exclude(status__isnull=False).exclude(date__isnull=True)
