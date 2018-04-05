from abc import ABCMeta, abstractmethod

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
        on_delete=models.SET_NULL,
        verbose_name=_('created by'),
        related_name="%(app_label)s_%(class)s_created_by")
    modified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        db_index=True,
        on_delete=models.SET_NULL,
        editable=False,
        verbose_name=_('modified by'),
        related_name="%(app_label)s_%(class)s_modified_by")

    def __str__(self):
        default = '{} #{}'.format(type(self).__name__, str(self.id))
        return getattr(self, 'name', getattr(self, 'title', default))

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


class CheckedModel(object):
    """
    Pre moderated models
    """
    pass


class CountryBase(ABCModel):
    """
    Base country class
    """

    @property
    @abstractmethod
    def countries(self):
        """
        Payment type countries
        """
        pass

    @property
    @abstractmethod
    def countries_excluded(self):
        """
        Payment type excluded countries
        """
        pass

    class Meta:
        abstract = True
