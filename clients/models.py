from annoying.fields import AutoOneToOneField
from django.core.exceptions import ValidationError
from django.core.validators import (MaxLengthValidator, MinLengthValidator,
                                    MinValueValidator, RegexValidator)
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django_extensions.db.models import TimeStampedModel
from djmoney.models.fields import MoneyField
from phonenumber_field.modelfields import PhoneNumberField

from billing.models import CommonInfo
from hotels.models import City, Country, Region

from .managers import ClientManager, ClientServiceManager


class Restrictions(CommonInfo, TimeStampedModel):
    """
    Client restrictions class
    """
    rooms_limit = models.PositiveIntegerField(
        verbose_name=_('rooms limit'), db_index=True, null=True, blank=True)

    client = AutoOneToOneField(
        'clients.Client',
        on_delete=models.CASCADE,
        related_name='restrictions',
        primary_key=True)

    class Meta:
        verbose_name_plural = _('restrictions')

    def __str__(self):
        return 'Client "{}" restrictions'.format(self.client)


class Client(CommonInfo, TimeStampedModel):
    """
    Client class
    """
    STATUSES = (('not_confirmed', _('not confirmed')), ('active', _('active')),
                ('disabled', _('disabled')), ('archived', _('archived')))

    INSTALLATION = (('not_installed', _('not installed')),
                    ('process', _('process')), ('installed', _('installed')))

    objects = ClientManager()

    login = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        verbose_name=_('login'),
        validators=[
            MinLengthValidator(4),
            RegexValidator(
                regex='^[a-z0-9\-]*$',
                code='invalid_login',
                message=_('Enter a valid login. This value may contain only \
lowercase letters, numbers, and "-" character.'))
        ])
    email = models.EmailField(
        db_index=True, unique=True, verbose_name=_('e-mail'))
    phone = PhoneNumberField(
        max_length=50,
        db_index=True,
        null=True,
        blank=True,
        verbose_name=_('phone'))
    name = models.CharField(
        max_length=255,
        db_index=True,
        validators=[MinLengthValidator(2)],
        verbose_name=_('full name'))
    description = models.TextField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name=_('description'),
        validators=[MinLengthValidator(2)])
    country = models.ForeignKey(
        Country,
        on_delete=models.PROTECT,
        verbose_name=_('country'),
        db_index=True)
    status = models.CharField(
        max_length=20,
        default='not_confirmed',
        choices=STATUSES,
        verbose_name=_('status'),
        db_index=True)
    installation = models.CharField(
        max_length=20,
        default='not_installed',
        verbose_name=_('installation status'),
        choices=INSTALLATION,
        db_index=True)
    disabled_at = models.DateTimeField(
        db_index=True, null=True, blank=True, verbose_name=_('disabled at'))
    url = models.URLField(
        db_index=True,
        null=True,
        blank=True,
        verbose_name=_('url'),
        help_text=_('maxibooking url'))
    ip = models.GenericIPAddressField(null=True, blank=True)

    def check_status(self):
        """
        Check client status
        """
        if self.status == 'disabled' and\
           not self.orders.get_expired(('archived',)).count():
            self.status = 'active'
            self.save()

    def restrictions_update(self, rooms=None):
        """
        Update client restrictions
        """
        if not rooms:
            rooms = Client.objects.count_rooms(client=self)
        self.restrictions.rooms_limit = rooms
        self.restrictions.save()

    def __str__(self):
        return '{} - {}'.format(self.login, self.name)

    class Meta:
        ordering = ['-created']


class Company(CommonInfo, TimeStampedModel):
    """
    Company class
    """
    FORMS = (
        ('ooo', _('ooo')),
        ('oao', _('oao')),
        ('ip', _('ip')),
        ('zao', _('zao')),
    )
    OPERATION_BASES = (
        ('charter', _('charter')),
        ('proxy', _('proxy')),
    )

    name = models.CharField(
        max_length=255,
        db_index=True,
        validators=[MinLengthValidator(2)],
        verbose_name=_('name'))
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        verbose_name=_('client'),
        db_index=True)
    form = models.CharField(
        max_length=20,
        default='active',
        choices=FORMS,
        null=True,
        blank=True,
        verbose_name=_('form'),
        db_index=True)
    ogrn = models.CharField(
        max_length=13,
        db_index=True,
        null=True,
        blank=True,
        validators=[MinLengthValidator(13),
                    MaxLengthValidator(13)],
        verbose_name=_('ogrn'))
    inn = models.CharField(
        max_length=12,
        db_index=True,
        null=True,
        blank=True,
        validators=[MinLengthValidator(10),
                    MaxLengthValidator(13)],
        verbose_name=_('inn'))
    kpp = models.CharField(
        max_length=9,
        db_index=True,
        null=True,
        blank=True,
        validators=[MinLengthValidator(9),
                    MaxLengthValidator(9)],
        verbose_name=_('kpp'))
    city = models.ForeignKey(
        City, on_delete=models.PROTECT, verbose_name=_('city'), db_index=True)
    region = models.ForeignKey(
        Region,
        on_delete=models.PROTECT,
        verbose_name=_('region'),
        db_index=True)
    address = models.CharField(
        max_length=255,
        db_index=True,
        validators=[MinLengthValidator(2)],
        verbose_name=_('address'))
    postal_code = models.CharField(
        max_length=100, db_index=True, validators=[MinLengthValidator(2)])
    account_number = models.CharField(
        max_length=100, db_index=True, validators=[MinLengthValidator(10)])
    bank = models.CharField(
        max_length=255,
        db_index=True,
        validators=[MinLengthValidator(2)],
        verbose_name=_('bank'))
    swift = models.CharField(
        max_length=255,
        db_index=True,
        validators=[MinLengthValidator(2)],
        verbose_name=_('swift'))
    bik = models.CharField(
        max_length=100,
        db_index=True,
        null=True,
        blank=True,
        validators=[MinLengthValidator(7)],
        verbose_name=_('bik'))
    corr_account = models.CharField(
        max_length=30,
        null=True,
        blank=True,
        validators=[MinLengthValidator(20),
                    MaxLengthValidator(30)],
        verbose_name=_('correspondent account'))
    boss_firstname = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        validators=[MinLengthValidator(2)],
        verbose_name=_('boss firstname'))
    boss_lastname = models.CharField(
        max_length=255,
        db_index=True,
        null=True,
        blank=True,
        validators=[MinLengthValidator(2)],
        verbose_name=_('boss lastname'))
    boss_patronymic = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        validators=[MinLengthValidator(2)],
        verbose_name=_('boss patronymic'))
    boss_operation_base = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        choices=OPERATION_BASES,
        verbose_name=_('boss operation base'))
    proxy_number = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        validators=[MinLengthValidator(2)],
        verbose_name=_('proxy number'))
    proxy_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('proxy date'),
    )

    class Meta:
        ordering = ['-created']
        unique_together = (('client', 'name'), )
        verbose_name_plural = _('companies')


class ClientService(CommonInfo, TimeStampedModel):
    """
    ClientService class
    """
    STATUSES = (('processing', _('processing')), ('active', _('active')))

    objects = ClientServiceManager()

    is_enabled = models.BooleanField(
        default=True, db_index=True, verbose_name=_('is enabled'))
    status = models.CharField(
        max_length=20,
        default='active',
        choices=STATUSES,
        verbose_name=_('status'),
        db_index=True)
    price = MoneyField(
        max_digits=20,
        decimal_places=2,
        blank=True,
        verbose_name=_('price'),
        validators=[MinValueValidator(0)],
        db_index=True)
    country = models.ForeignKey(
        Country,
        blank=True,
        on_delete=models.PROTECT,
        verbose_name=_('country'),
        db_index=True,
        related_name='client_services')
    quantity = models.PositiveIntegerField(
        verbose_name=_('quantity'),
        db_index=True,
        validators=[MinValueValidator(1)])
    start_at = models.DateTimeField(
        db_index=True, verbose_name=_('start date'), auto_now_add=True)
    begin = models.DateTimeField(
        db_index=True, blank=True, verbose_name=_('begin date'))
    end = models.DateTimeField(
        db_index=True, blank=True, verbose_name=_('end date'))
    service = models.ForeignKey(
        'finances.Service',
        on_delete=models.PROTECT,
        db_index=True,
        verbose_name=_('service'),
        related_name='client_services')
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        db_index=True,
        verbose_name=_('client'),
        related_name='services')
    orders = models.ManyToManyField(
        'finances.Order', verbose_name=_('orders'), blank=True)

    def price_repr(self):
        return '{} {}'.format(
            getattr(self.price, 'amount', ''), self.price.currency)

    price_repr.short_description = _('price')

    def get_default_begin(self):
        """
        Get default begin for client_service
        """
        prev = ClientService.objects.get_prev(self)
        if prev:
            return prev.end

        return self.service.get_default_begin()

    def save(self, *args, **kwargs):
        self.price = self.service.get_price(client=self.client) * self.quantity

        if self.begin is None:
            self.begin = self.get_default_begin()
        if self.end is None:
            self.end = self.service.get_default_end(self.begin)
        if self.country_id is None:
            self.country = self.client.country
        if self.start_at is None:
            self.start_at = timezone.now()
        super(ClientService, self).save(*args, **kwargs)

        if self.is_enabled:
            ClientService.objects.disable(
                client=self.client,
                service_type=self.service.type,
                exclude_pk=self.pk)

    @staticmethod
    def validate_dates(begin, end, is_new):
        if is_new and begin and begin < timezone.now():
            raise ValidationError(_('Please correct begin date.'))
        if begin and end and begin > end:
            raise ValidationError(_('Please correct dates.'))

    @staticmethod
    def validate_service(service, client):
        if service and not service.get_price(client=client):
            raise ValidationError(_('Empty service prices.'))

    def clean(self):
        ClientService.validate_dates(self.begin, self.end, self.pk is None)
        ClientService.validate_service(self.service, self.client)

    def validate_unique(self, exclude=None):
        super(ClientService, self).validate_unique(exclude)
        service = self.service

        if service.type != 'other' and ClientService.objects.filter(
                client=self.client,
                service__type=service.type,
                service__period=service.period,
                service__period_units=service.period_units,
                is_enabled=True).exclude(id=self.id).exists():
            raise ValidationError(
                _('Client service with this type already exists.'))

    def __str__(self):
        return '#{} - {} - {} - {}'.format(self.id, self.client, self.service,
                                           self.price)

    class Meta:
        ordering = ['-created']
        unique_together = (('client', 'is_enabled', 'service'), )
