import logging
import random
import string

import arrow
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.postgres.fields import JSONField
from django.core.validators import (MaxValueValidator, MinLengthValidator,
                                    MinValueValidator, ValidationError)
from django.db import models
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
from django_extensions.db.models import TimeStampedModel, TitleDescriptionModel
from djmoney.models.fields import MoneyField
from djmoney.models.validators import MinMoneyValidator
from model_utils import FieldTracker
from moneyed import EUR, Money

from billing.exceptions import BaseException
from billing.lib.lang import get_lang
from billing.models import CachedModel, CommonInfo
from clients.models import Client, ClientService
from finances.systems.lib import BraintreeGateway
from hotels.models import Country
from users.models import Department

from .managers import (DiscountManager, OrderManager, PriceManager,
                       ServiceManager, SubscriptionManager)
from .validators import validate_code, validate_price_periods


class ServiceCategory(CommonInfo, TimeStampedModel, TitleDescriptionModel):
    """
    ServiceCategory class
    """

    class Meta:
        ordering = ['title']
        verbose_name_plural = _('service categories')


class Service(CachedModel, CommonInfo, TimeStampedModel,
              TitleDescriptionModel):
    """
    Service class
    """
    # PERIODS_UNITS = (('day', _('day')), ('month', _('month')), ('year',
    #                                                             _('year')))
    # PERIODS_UNITS_TO_DAYS = {'day': 1, 'month': 31, 'year': 365}

    PERIODS_UNITS = (('month', _('month')), ('year', _('year')))
    PERIODS_UNITS_TO_DAYS = {'month': 31, 'year': 365}

    TYPES = (('rooms', _('rooms')), ('other', _('other')))

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
    category = models.ForeignKey(
        ServiceCategory,
        on_delete=models.CASCADE,
        verbose_name=_('category'),
        db_index=True,
        related_name='services',
    )

    @property
    def period_in_months(self):
        if self.period_units == 'month':
            return self.period
        if self.period_units == 'year':
            return self.period * 12

    @property
    def price_money(self):
        try:
            return self.prices.filter(
                country__isnull=True,
                is_enabled=True,
                period_from__isnull=True,
                period_to__isnull=True,
            )[0].price
        except IndexError:
            return None

    @property
    def price(self):
        return getattr(self.price_money, 'amount', None)

    @property
    def price_currency(self):
        return getattr(
            getattr(self.price_money, 'currency', None), 'code', None)

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


class Price(CachedModel, CommonInfo, TimeStampedModel):
    """
    Price class
    """
    objects = PriceManager()

    price = MoneyField(
        max_digits=20,
        decimal_places=2,
        verbose_name=_('price'),
        validators=[MinMoneyValidator(0)],
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
    period_from = models.PositiveIntegerField(
        db_index=True,
        null=True,
        blank=True,
        verbose_name=_('from'),
    )
    period_to = models.PositiveIntegerField(
        db_index=True,
        null=True,
        blank=True,
        verbose_name=_('to'),
    )
    for_unit = models.BooleanField(
        default=True, db_index=True, verbose_name=_('for unit'))

    def __str__(self):
        return '{}: {} {}-{} {}'.format(
            self.country if self.country else 'Base',
            self.price,
            self.period_from or '∞',
            self.period_to or '∞',
            'per unit' if self.for_unit else 'per period',
        )

    def clean(self):
        """
        Price validation
        """
        validate_price_periods(self)

    class Meta:
        ordering = ['country', 'period_from', 'period_to', 'price']
        unique_together = ('service', 'country', 'period_from', 'period_to')


class DiscountBase(CommonInfo, TimeStampedModel, TitleDescriptionModel):

    start_date = models.DateTimeField(
        db_index=True, null=True, blank=True, verbose_name=_('begin date'))
    end_date = models.DateTimeField(
        db_index=True, null=True, blank=True, verbose_name=_('end date'))
    manager = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        verbose_name=_('manager'),
        db_index=True,
        related_name='%(app_label)s_%(class)s_discounts',
        null=True,
        blank=True)
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        verbose_name=_('department'),
        related_name='%(app_label)s_%(class)s_discounts',
        null=True,
        blank=True,
        db_index=True)
    number_of_uses = models.PositiveIntegerField(
        verbose_name=_('number of uses'),
        db_index=True,
        default=1,
        help_text=_(
            'To how many orders per user can this discount be applied'))
    percentage_discount = models.FloatField(
        verbose_name=_('percentage discount'),
        validators=[MinValueValidator(0),
                    MaxValueValidator(100)],
        db_index=True,
    )
    code = models.CharField(
        max_length=20,
        blank=True,
        null=False,
        unique=True,
        validators=[MinLengthValidator(5), validate_code],
        help_text=_('The unique code of the discount'),
    )

    def clean(self):
        """
        Department validation
        """
        if not self.start_date or not self.end_date:
            return None
        if self.start_date > self.end_date:
            raise ValidationError('The start date cannot be greater \
than the end date')

    def __str__(self):
        return '#{} {}'.format(self.id, self.title)

    class Meta:
        abstract = True


class Discount(DiscountBase):
    """
    Discount class
    """

    objects = DiscountManager()

    def update_prices(self):
        """
        Update discount prices according related department
        """
        if self.department:
            department = self.department
        elif self.manager:
            department = self.manager.profile.department
        else:
            department = None

        if not department:
            return self

        if department.max_percentage_discount:
            self.percentage_discount = min(
                self.percentage_discount,
                department.max_percentage_discount,
            )
        if department.min_percentage_discount:
            self.percentage_discount = max(
                self.percentage_discount,
                department.min_percentage_discount,
            )
        return self

    def get_code(self, user=None):
        user = self.manager if self.manager else user
        if not user or not user.profile.code:
            raise ValueError('valid user is not defined')
        if not self.code:
            raise ValueError('discount has no code')
        user_code = user.profile.code

        return '{}~{}'.format(user_code, self.code)

    def generate_code(self):
        """
        Generate a unique code for the discount
        """
        code = ''.join(
            random.choices(string.ascii_lowercase + string.digits, k=8))
        user_id = self.manager.id if self.manager else 0
        department_id = self.department.id if self.department else 0
        self.code = '{}{}{}'.format(department_id, user_id, code)

    class Meta:
        permissions = (
            ('change_own_discount', _('Can change only own discounts')),
            ('delete_any_discount', _('Can delete any discounts')),
            ('change_department_discount',
             _('Can change only department discounts')),
        )


class ClientDiscount(DiscountBase):
    """
    Discount spanshot for client
    """
    client = models.OneToOneField(
        Client, on_delete=models.CASCADE, related_name='discount')
    original_discount = models.ForeignKey(
        Discount,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='client_discount')
    usage_count = models.PositiveIntegerField(
        db_index=True,
        default=0,
        help_text=_(
            'The number of times the discount has already been applied'))

    @property
    def remaining_uses(self):
        return self.number_of_uses - self.usage_count

    @staticmethod
    def client_spanshot(discount, client):
        if not discount:
            return None
        snapshot = ClientDiscount()
        values = discount.__dict__.copy()
        remove = [
            '_state', 'id', 'created', 'updated', 'created_by_id',
            'updated_by_id'
        ]
        for k in remove:
            values.pop(k, None)
        snapshot.__dict__.update(values)
        try:
            snapshot.client = client
            snapshot.original_discount_id = discount.id
            snapshot.full_clean()
            snapshot.save()
            return snapshot
        except ValidationError:
            return None


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
        validators=[MinMoneyValidator(0)],
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
        max_length=30,
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
    discount = models.ForeignKey(
        ClientDiscount,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_index=True,
        related_name='orders')

    @property
    def get_room_service(self):
        client_service = self.client_services.filter(
            service__type='rooms', service__period_units__in=('month',
                                                              'year')).first()
        return getattr(client_service, 'service', None)

    @property
    def client_services_by_category(self):
        """
        Grouped services
        """
        return self.client_services.get_order_services_by_category(self)

    def get_payer(self, client_filter=None, local=True):
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
        if not local:
            return client

    def calc_price(self):
        """
        Calculate && return price
        """
        if self.status == 'corrupted':
            return Money(0, EUR)
        price = self.client_services.total(self.client_services)
        return self.apply_discount(price)

    def apply_discount(self, price):
        """
        Apply the client discount to the price
        """
        discount = getattr(self.client, 'discount', None)
        now = arrow.utcnow().datetime
        skip = False

        if not discount or not price:
            return price

        if not discount.remaining_uses:
            skip = True

        if discount.start_date and discount.start_date > now:
            skip = True

        if discount.end_date and discount.end_date < now:
            skip = True

        if discount == self.discount:
            skip = False

        if skip:
            return price

        price = price * (100 - discount.percentage_discount) / 100
        if discount != self.discount:
            discount.usage_count += 1
        self.discount = discount
        discount.save()

        return price

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

    @property
    def price_str(self):
        return '{} {}'.format(self.price.amount, self.price.currency)

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
        permissions = (('list_manager', _('Can see assigned entries')), )


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
        vals = data if isinstance(data, dict) else vars(data)
        self.data = {k: str(v) for k, v in vals.items()}

    class Meta:
        ordering = (
            '-modified',
            '-created',
        )


class Subscription(CommonInfo, TimeStampedModel):
    """
    The class represents client subscriptions
    """
    objects = SubscriptionManager()

    STATUSES = (
        ('enabled', _('enabled')),
        ('canceled', _('canceled')),
    )
    client = models.ForeignKey(
        Client,
        on_delete=models.PROTECT,
        db_index=True,
        verbose_name=_('client'),
        related_name='subscriptions')
    order = models.ForeignKey(
        Order,
        on_delete=models.SET_NULL,
        verbose_name=_('order'),
        null=True,
        blank=True,
        db_index=True,
        related_name='subscriptions')
    country = models.ForeignKey(
        Country,
        on_delete=models.PROTECT,
        verbose_name=_('country'),
        db_index=True,
        related_name='subscriptions')
    status = models.CharField(
        max_length=20,
        default='enabled',
        choices=STATUSES,
        verbose_name=_('status'),
        db_index=True)
    price = MoneyField(
        max_digits=20,
        decimal_places=2,
        blank=True,
        verbose_name=_('price'),
        validators=[MinMoneyValidator(0)],
        db_index=True)
    period = models.PositiveIntegerField(
        verbose_name=_('period'),
        db_index=True,
        help_text=_('the billing period in months'))
    merchant = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        db_index=True,
        verbose_name=_('merchant'),
    )
    customer = models.CharField(
        max_length=255,
        db_index=True,
        verbose_name=_('customer'),
    )
    subscription = models.CharField(
        max_length=255,
        db_index=True,
        verbose_name=_('subscription'),
    )

    def cancel(self):
        """
        Cancel the subscription
        """
        braintree = BraintreeGateway(self.country, 'sandbox')
        result = braintree.cancel_subscription(self.subscription)
        if (result):
            self.status = 'canceled'
            self.save()

    def save(self, *args, **kwargs):
        if self.status == 'enabled':
            for subscription in Subscription.objects.get_active(
                    self.client, self.pk):
                subscription.cancel()
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-created']
