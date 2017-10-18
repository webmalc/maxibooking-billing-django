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
        max_length=255, db_index=True, verbose_name=_('end date'))

    class Meta:
        abstract = True


class Fms(FmsMixin):
    pass


class Kpp(FmsMixin):
    pass
