from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django_extensions.db.models import TimeStampedModel, TitleDescriptionModel

from billing.models import CommonInfo
from clients.models import Client
from hotels.models import Country


class Service(CommonInfo, TimeStampedModel, TitleDescriptionModel):
    """
    Service class
    """
    PERIODS_UNITS = (('day', _('day')), ('month', _('month')),
                     ('year', _('year')))
    PERIODS_UNITS_TO_DAYS = {'day': 1, 'month': 31, 'year': 365}

    is_enabled = models.BooleanField(
        default=True, db_index=True, verbose_name=_('is enabled'))
    period = models.PositiveIntegerField(
        verbose_name=_('period'), db_index=True)
    period_units = models.CharField(
        verbose_name=_('units of period'),
        max_length=20,
        default='month',
        choices=PERIODS_UNITS,
        db_index=True)

    @property
    def price(self):
        try:
            return self.prices.filter(
                country__isnull=True, is_enabled=True)[0].price
        except IndexError:
            return None

    def get_price(self, country=None, client=None):
        """
        Get price by country or client
        """
        if isinstance(client, int) or (isinstance(client, str) and
                                       client.isnumeric()):
            try:
                client = Client.objects.get(pk=int(client))
            except Client.DoesNotExist:
                pass
        if isinstance(client, Client):
            country = client.country

        if country:
            query = self.prices.filter(is_enabled=True)
            if isinstance(country, int) or (isinstance(country, str) and
                                            country.isnumeric()):
                query = query.filter(country__id=int(country))
            elif isinstance(country, Country):
                query = query.filter(country=country)
            else:
                query = query.filter(country__tld=country)
            try:
                return query[0].price
            except IndexError:
                pass

        return self.price

    @property
    def period_days(self):
        return self.period * self.PERIODS_UNITS_TO_DAYS.get(
            self.period_units, 0) if self.period else 0

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['title']
        unique_together = ('title', 'is_enabled')


class Price(CommonInfo, TimeStampedModel):
    """
    Price class
    """
    price = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        verbose_name=_('price'),
        validators=[MinValueValidator(0)],
        db_index=True)
    country = models.ForeignKey(
        Country,
        on_delete=models.PROTECT,
        verbose_name=_('country'),
        null=True,
        blank=True,
        db_index=True)
    is_enabled = models.BooleanField(
        default=True, db_index=True, verbose_name=_('is enabled'))
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        verbose_name=_('service'),
        db_index=True,
        related_name='prices')

    def __str__(self):
        return '{}: {}'.format(self.country
                               if self.country else 'Base', self.price)

    def clean(self):
        """
        Price validation
        """
        if not self.country and Price.objects.filter(
                service=self.service,
                country__isnull=True).exclude(id=self.id).exists():
            raise ValidationError('Base price already exists')

    class Meta:
        ordering = ['price']
        unique_together = ('service', 'country')
