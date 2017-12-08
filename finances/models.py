import logging

import arrow
from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.core.validators import MinValueValidator, ValidationError
from django.db import models
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
from django_extensions.db.models import TimeStampedModel, TitleDescriptionModel
from djmoney.models.fields import MoneyField
from model_utils import FieldTracker
from moneyed import EUR, Money

from billing.exceptions import BaseException
from billing.lib.lang import get_lang
from billing.models import CommonInfo
from clients.models import Client, ClientService
from hotels.models import Country

from .managers import OrderManager, ServiceManager


class Service(CommonInfo, TimeStampedModel, TitleDescriptionModel):
    """
    Service class
    """
    PERIODS_UNITS = (('day', _('day')), ('month', _('month')), ('year',
                                                                _('year')))
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
    default_rooms = models.PositiveIntegerField(
        verbose_name=_('default rooms'), db_index=True, null=True, blank=True)
    type = models.CharField(
        verbose_name=_('type'),
        max_length=20,
        default='other',
        choices=TYPES,
        db_index=True)

    @property
    def price_money(self):
        try:
            return self.prices.filter(
                country__isnull=True, is_enabled=True)[0].price
        except IndexError:
            return None

    @property
    def price(self):
        return getattr(self.price_money, 'amount', None)

    @property
    def price_currency(self):
        return getattr(
            getattr(self.price_money, 'currency', None), 'code', None)

    def get_price(self, country=None, client=None):
        """
        Get price by country or client
        """
        if isinstance(client, int) or \
           (isinstance(client, str) and client.isnumeric()):
            try:
                client = Client.objects.get(pk=int(client))
            except Client.DoesNotExist:
                pass
        if isinstance(client, Client):
            country = client.country

        if country:
            query = self.prices.filter(is_enabled=True)
            if isinstance(country, int) or \
               (isinstance(country, str) and country.isnumeric()):
                query = query.filter(country__id=int(country))
            elif isinstance(country, Country):
                query = query.filter(country=country)
            else:
                query = query.filter(country__tld=country)
            try:
                return query[0].price
            except IndexError:
                pass

        return self.price_money

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
        if self.is_default and self.type != 'other' and Service.objects.filter(
                type=self.type, is_enabled=True,
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
    price = MoneyField(
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
    STATUSES = (
        ('new', _('new')),
        ('processing', _('processing')),
        ('paid', _('paid')),
        ('canceled', _('canceled')),
        ('corrupted', _('corrupted')),
    )
    objects = OrderManager()
    tracker = FieldTracker()

    status = models.CharField(
        max_length=20,
        default='new',
        choices=STATUSES,
        verbose_name=_('status'),
        db_index=True)
    note = models.TextField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name=_('note'),
        help_text=_('Clear to regenerate note'))
    price = MoneyField(
        max_digits=20,
        decimal_places=2,
        default=0,
        verbose_name=_('price'),
        validators=[MinValueValidator(0)],
        db_index=True,
        help_text=_('Set zero to recalculate price'))
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
    payment_system = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        choices=[(s, _(s)) for s in settings.PAYMENT_SYSTEMS],
        verbose_name=_('payment system'),
        db_index=True)
    client_services = models.ManyToManyField(
        'clients.ClientService',
        blank=True,
        verbose_name=_('client services'),
        through=ClientService.orders.through)

    def get_payer(self, client_filter=None):
        """
        Return payer
        """
        company = self.client.get_bill_company()
        client = self.client
        if client_filter:
            if not all([getattr(client, f, None) for f in client_filter]):
                client = None
        lang = get_lang(self.client.country.tld)
        local_company = getattr(company, lang, None)
        local_client = getattr(client, lang, None)

        if local_company:
            return company
        if local_client:
            return client

    def calc_price(self):
        """
        Calculate && return price
        """
        if self.status == 'corrupted':
            return Money(0, EUR)
        return self.client_services.total(self.client_services)

    def set_corrupted(self):
        """
        Set corrupted orders
        """
        if len(set([s.price.currency
                    for s in self.client_services.all()])) > 1:
            self.status = 'corrupted'
            self.price = self.calc_price()
            self.save()
            logger = logging.getLogger('billing')
            logger.error('Order corrupted #{}.'.format(self.pk))

    def set_paid(self, payment_system):
        """
        Set paid orders
        """
        self.status = 'paid'
        self.payment_system = payment_system
        self.paid_date = arrow.utcnow().datetime
        self.full_clean()
        self.save()

    def generate_note(self):
        """
        Generate and return default order note
        """
        if self.client_services.count():
            return render_to_string('finances/order_note.md', {'order': self})
        return None

    def clean(self, *args, **kwargs):
        if self.status == 'paid' and \
           (not self.payment_system or not self.paid_date):
            raise ValidationError({
                'status':
                _('Can`t set "paid" status with empty payment system \
and paid date')
            })
        super(Order, self).clean(*args, **kwargs)

    def __str__(self):
        return '#{} - {} - {} - {} - {}'.format(
            self.id, self.status, self.client, self.price,
            self.expired_date.strftime('%c'))

    class Meta:
        ordering = (
            '-modified',
            '-created',
        )


class Transaction(CommonInfo, TimeStampedModel):
    """
    Payment systems transaction model
    """
    order = models.ForeignKey(
        Order,
        on_delete=models.SET_NULL,
        verbose_name=_('order'),
        null=True,
        blank=True,
        db_index=True,
        related_name='transactions')
    data = JSONField(verbose_name=_('transaction'))

    def set_data(self, data):
        self.data = data if isinstance(data, dict) else vars(data)

    class Meta:
        ordering = (
            '-modified',
            '-created',
        )
