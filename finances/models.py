from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django_extensions.db.models import TimeStampedModel, TitleDescriptionModel

from billing.models import CommonInfo


class Service(CommonInfo, TimeStampedModel, TitleDescriptionModel):
    """
    Service class
    """
    PERIODS_UNITS = (('day', _('day')), ('month', _('month')),
                     ('year', _('year')))
    PERIODS_UNITS_TO_DAYS = {'day': 1, 'month': 31, 'year': 365}

    is_enabled = models.BooleanField(
        default=True, db_index=True, verbose_name=_('is enabled'))
    price = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        verbose_name=_('price'),
        validators=[MinValueValidator(0)],
        db_index=True)

    period = models.PositiveIntegerField(
        verbose_name=_('period'), db_index=True)
    period_units = models.CharField(
        verbose_name=_('units of period'),
        max_length=20,
        default='month',
        choices=PERIODS_UNITS,
        db_index=True)

    @property
    def period_days(self):
        return self.period * self.PERIODS_UNITS_TO_DAYS.get(
            self.period_units, 0) if self.period else 0

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['title']
        unique_together = ('title', 'is_enabled')
