from abc import ABCMeta

from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _


class CommonInfo(models.Model):
    """ CommonInfo abstract model """

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        db_index=True,
        on_delete=models.CASCADE,
        verbose_name=_('created by'),
        related_name="%(app_label)s_%(class)s_created_by")
    modified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        db_index=True,
        on_delete=models.CASCADE,
        editable=False,
        verbose_name=_('modified by'),
        related_name="%(app_label)s_%(class)s_modified_by")

    def __str__(self):
        return getattr(self, 'name', '{} #{}'.format(
            type(self).__name__, str(self.id)))

    class Meta:
        abstract = True


class AbstractModelMeta(ABCMeta, type(models.Model)):
    pass


class ABCModel(models.Model):
    """
    Abstract Django model
    """
    __metaclass__ = AbstractModelMeta

    class Meta:
        abstract = True


class CachedModel(models.Model):
    class Meta:
        abstract = True
