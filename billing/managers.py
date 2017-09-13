from abc import ABCMeta, abstractproperty
from functools import reduce

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
