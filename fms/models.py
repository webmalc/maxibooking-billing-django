from django.db import models
from django.utils.translation import ugettext_lazy as _
from django_extensions.db.models import TimeStampedModel

from billing.models import CommonInfo


class FmsMixin(CommonInfo, TimeStampedModel):
    internal_id = models.CharField(
        max_length=100, db_index=True, verbose_name=_('internal_id'))
    name = models.CharField(
        max_length=255, db_index=True, verbose_name=_('name'))
    code = models.CharField(
        max_length=255, db_index=True, verbose_name=_('code'))
    end_date = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        db_index=True,
        verbose_name=_('end date'))

    class Meta:
        abstract = True


class Fms(FmsMixin):
    class Meta:
        verbose_name_plural = _('fms')
        unique_together = (('internal_id', 'name', 'code'))


class Kpp(FmsMixin):
    class Meta:
        verbose_name_plural = _('kpp')
        unique_together = (('internal_id', 'name', 'code'))
