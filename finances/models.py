import arrow
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
from django_extensions.db.models import TimeStampedModel, TitleDescriptionModel
from model_utils import FieldTracker

from billing.exceptions import BaseException
from billing.models import CommonInfo
from clients.models import Client, ClientService
from hotels.models import Country

from .managers import ServiceManager


class Service(CommonInfo, TimeStampedModel, TitleDescriptionModel):
    """
    Service class
    """
    PERIODS_UNITS = (('day', _('day')), ('month', _('month')),
                     ('year', _('year')))
    PERIODS_UNITS_TO_DAYS = {'day': 1, 'month': 31, 'year': 365}
    TYPES = (('connection', _('connection')), ('rooms', _('rooms')),
             ('other', _('other')))

    objects = ServiceManager()

    is_enabled = models.BooleanField(
        default=True, db_index=True, verbose_name=_('is enabled'))
    is_default = models.BooleanField(
        default=False, db_index=True, verbose_name=_('is default'))
    period = models.PositiveIntegerField(
        verbose_name=_('period'), db_index=True)
    period_units = models.CharField(
        verbose_name=_('units of period'),
        max_length=20,
        default='month',
        choices=PERIODS_UNITS,
        db_index=True)
    type = models.CharField(
        verbose_name=_('type'),
        max_length=20,
        default='other',
        choices=TYPES,
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

    def get_default_end(self, begin=None):
        end = arrow.get(begin) if begin else arrow.utcnow()
        if self.period_units == 'day':
            end = end.shift(days=self.period)
        elif self.period_units == 'month':
            end = end.shift(months=self.period)
        elif self.period_units == 'year':
            end = end.shift(years=self.period)
        else:
            raise BaseException('Unsupported service period units')
        return end.datetime

    def get_default_begin(self):
        return arrow.utcnow().datetime

    def __str__(self):
        return self.title

    def validate_unique(self, exclude=None):
        super(Service, self).validate_unique(exclude)
        service_type = self.type
        if service_type != 'other' and Service.objects.filter(
                type=service_type, is_enabled=True,
                is_default=True).exclude(id=self.id).exists():
            raise ValidationError(
                _('Default service with this type already exists.'))

    class Meta:
        ordering = ['title']
        unique_together = (('title', 'is_enabled'),
                           ('type', 'period', 'period_units', 'is_enabled'))


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
                service=self.service, country__isnull=True,
                is_enabled=True).exclude(id=self.id).exists():
            raise ValidationError('Base price already exists')

    class Meta:
        ordering = ['price']
        unique_together = ('service', 'country')


class Order(CommonInfo, TimeStampedModel):
    """
    Order class
    """
    tracker = FieldTracker()

    STATUSES = (('new', _('new')), ('processing', _('processing')),
                ('paid', _('paid')), ('canceled', _('canceled')))
    status = models.CharField(
        max_length=20,
        default='active',
        choices=STATUSES,
        verbose_name=_('status'),
        db_index=True)
    note = models.TextField(blank=True, db_index=True, verbose_name=_('note'))
    price = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        blank=True,
        verbose_name=_('price'),
        validators=[MinValueValidator(0)],
        db_index=True,
        help_text=_('Delete to recalculate price'))
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        db_index=True,
        verbose_name=_('client'),
        related_name='orders')
    expired_date = models.DateTimeField(
        db_index=True, blank=True, verbose_name=_('expired date'))
    paid_date = models.DateTimeField(
        db_index=True, null=True, blank=True, verbose_name=_('paid date'))
    client_services = models.ManyToManyField(
        'clients.ClientService',
        verbose_name=_('client services'),
        through=ClientService.orders.through)

    def calc_price(self):
        """
        Calculate && return price
        """
        return self.client_services.total(self.client_services)

    def generate_note(self):
        """
        Generate and return default order note
        """
        return render_to_string('finances/order_note.md', {'order': self})

    def clean(self):
        if not self.price and not self.client_services.count():
            raise ValidationError(_('Empty price and client services.'))

    def save(self, *args, **kwargs):
        # calculate price
        if not self.price:
            self.price = self.calc_price()

        # generate note
        if not self.note:
            self.note = self.generate_note()

        # set expired date
        if not self.expired_date:
            self.expired_date = arrow.utcnow().shift(
                days=+settings.MB_ORDER_EXPIRED_DAYS).datetime

        # send notification to client

        # set paid date && update services

        super(Order, self).save(*args, **kwargs)

    def __str__(self):
        return '#{} - {} - {} - {} - {}'.format(
            self.id, self.status, self.client, self.price,
            self.expired_date.strftime('%c'))
