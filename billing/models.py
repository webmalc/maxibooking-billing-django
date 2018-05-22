from abc import ABCMeta, abstractmethod

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.validators import MinLengthValidator
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django_extensions.db.models import TimeStampedModel, TitleDescriptionModel

from .managers import CommentsManager, DictManager


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


class Comment(CommonInfo, TimeStampedModel):
    """
    Client comment class
    """
    TYPES = (
        ('message', _('message')),
        ('refusal', _('refusal')),
        ('action', _('action')),
    )
    STATUSES = (
        ('completed', _('completed')),
        ('canceled', _('canceled')),
    )
    objects = CommentsManager()

    text = models.TextField(
        db_index=True,
        validators=[MinLengthValidator(2)],
        verbose_name=_('text'))
    date = models.DateTimeField(
        verbose_name=_('date'),
        null=True,
        blank=True,
    )
    status = models.CharField(
        verbose_name=_('status'),
        max_length=20,
        choices=STATUSES,
        null=True,
        blank=True,
        db_index=True,
    )
    type = models.CharField(
        verbose_name=_('type'),
        max_length=20,
        choices=TYPES,
        default='message',
        db_index=True,
    )

    def __str__(self):
        date = self.modified if self.modified else self.created
        return '{} {}'.format(
            self.modified_by,
            date.strftime('%d.%m.%Y %H:%M'),
        )

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()

    class Meta:
        ordering = ['-created']


class DictMixin(CommonInfo, TimeStampedModel, TitleDescriptionModel):
    """
    Mixin for dict models
    """
    code = models.CharField(
        verbose_name=_('code'),
        max_length=20,
        null=True,
        blank=True,
        editable=False,
        db_index=True,
        unique=True,
    )
    is_enabled = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name=_('is enabled'),
    )
    objects = DictManager()

    class Meta:
        abstract = True
        ordering = ['title']


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
