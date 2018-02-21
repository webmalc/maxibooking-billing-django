from annoying.fields import AutoOneToOneField
from django.core.exceptions import ValidationError
from django.core.validators import (MaxLengthValidator, MinLengthValidator,
                                    MinValueValidator, RegexValidator,
                                    integer_validator)
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django_extensions.db.models import TimeStampedModel
from djmoney.models.fields import MoneyField
from phonenumber_field.modelfields import PhoneNumberField

from billing.models import CommonInfo, CountryBase
from hotels.models import Country

from .managers import ClientManager, ClientServiceManager, CompanyManager
from .validators import validate_client_login_restrictions


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


class Payer():
    @property
    def text(self):
        """
        Payer text representation
        """
        raise NotImplementedError()


class Company(CommonInfo, TimeStampedModel, Payer):
    """
    Company base class
    """

    objects = CompanyManager()

    name = models.CharField(
        max_length=255,
        db_index=True,
        validators=[MinLengthValidator(2)],
        verbose_name=_('name'))
    client = models.ForeignKey(
        'clients.Client',
        on_delete=models.CASCADE,
        verbose_name=_('client'),
        related_name='companies',
        db_index=True)
    account_number = models.CharField(
        max_length=50, db_index=True, validators=[MinLengthValidator(10)])
    city = models.ForeignKey(
        'hotels.City',
        on_delete=models.PROTECT,
        verbose_name=_('city'),
        db_index=True)
    region = models.ForeignKey(
        'hotels.Region',
        on_delete=models.PROTECT,
        verbose_name=_('region'),
        db_index=True)
    address = models.CharField(
        max_length=255,
        db_index=True,
        validators=[MinLengthValidator(2)],
        verbose_name=_('address'))
    postal_code = models.CharField(
        max_length=50, db_index=True, validators=[MinLengthValidator(2)])

    bank = models.CharField(
        max_length=255,
        db_index=True,
        validators=[MinLengthValidator(2)],
        verbose_name=_('bank'))

    @property
    def text(self):
        return '{form} {name}, ИНН {inn}, КПП {kpp}, \
        {postal_code}, {region}, {city}, {address}'.format(
            form=self.ru.get_form_display(),
            name=self.name,
            inn=self.ru.inn,
            kpp=self.ru.kpp,
            postal_code=self.postal_code,
            region=self.city.name,
            city=self.region.name,
            address=self.address,
        )

    class Meta:
        ordering = ['-created']
        unique_together = (('client', 'name'), )
        verbose_name_plural = _('companies')


class CompanyWorld(CountryBase):
    """
    Company world class
    """
    countries_excluded = ['ru']
    countries = []

    swift = models.CharField(
        max_length=20,
        db_index=True,
        validators=[
            MinLengthValidator(8),
            integer_validator,
        ],
        verbose_name=_('swift'))
    company = models.OneToOneField(
        Company,
        on_delete=models.CASCADE,
        related_name='world',
        primary_key=True)

    class Meta:
        verbose_name_plural = _('world')
        verbose_name = _('world')


class CompanyRu(CountryBase):
    """
    Company ru class
    """
    countries_excluded = []
    countries = ['ru']

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

    form = models.CharField(
        max_length=20, choices=FORMS, verbose_name=_('form'), db_index=True)
    ogrn = models.CharField(
        max_length=13,
        db_index=True,
        validators=[
            MinLengthValidator(13),
            MaxLengthValidator(13),
            integer_validator,
        ],
        verbose_name=_('ogrn'))
    inn = models.CharField(
        max_length=13,
        db_index=True,
        validators=[
            MinLengthValidator(10),
            MaxLengthValidator(13),
            integer_validator,
        ],
        verbose_name=_('inn'))
    kpp = models.CharField(
        max_length=9,
        db_index=True,
        validators=[
            MinLengthValidator(9),
            MaxLengthValidator(9),
            integer_validator,
        ],
        verbose_name=_('kpp'))

    bik = models.CharField(
        max_length=30,
        db_index=True,
        validators=[
            MinLengthValidator(7),
            integer_validator,
        ],
        verbose_name=_('bik'))
    corr_account = models.CharField(
        max_length=30,
        validators=[
            MinLengthValidator(20),
            MaxLengthValidator(30),
            integer_validator,
        ],
        verbose_name=_('correspondent account'))
    boss_firstname = models.CharField(
        max_length=255,
        validators=[MinLengthValidator(2)],
        verbose_name=_('boss firstname'))
    boss_lastname = models.CharField(
        max_length=255,
        db_index=True,
        validators=[MinLengthValidator(2)],
        verbose_name=_('boss lastname'))
    boss_patronymic = models.CharField(
        max_length=255,
        validators=[MinLengthValidator(2)],
        verbose_name=_('boss patronymic'))
    boss_operation_base = models.CharField(
        max_length=255,
        choices=OPERATION_BASES,
        verbose_name=_('boss operation base'))
    proxy_number = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        validators=[
            MinLengthValidator(2),
            integer_validator,
        ],
        verbose_name=_('proxy number'))
    proxy_date = models.DateTimeField(
        verbose_name=_('proxy date'),
        null=True,
        blank=True,
    )
    company = models.OneToOneField(
        Company, on_delete=models.CASCADE, related_name='ru', primary_key=True)

    def clean(self):
        if self.boss_operation_base == 'proxy' and\
           not all([self.proxy_number, self.proxy_date]):
            raise ValidationError(
                _('Please fill proxy date and proxy number.'))

    class Meta:
        verbose_name_plural = _('ru')
        verbose_name = _('ru')


class Client(CommonInfo, TimeStampedModel, Payer):
    """
    Client class
    """
    STATUSES = (('not_confirmed', _('not confirmed')), ('active', _('active')),
                ('disabled', _('disabled')), ('archived', _('archived')))

    INSTALLATION = (('not_installed', _('not installed')), ('process',
                                                            _('process')),
                    ('installed', _('installed')))

    objects = ClientManager()

    login = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        error_messages={'unique': _('Client with this domain already exist.')},
        verbose_name=_('login'),
        validators=[
            MinLengthValidator(4),
            RegexValidator(
                regex='^[a-z0-9\-]*$',
                code='invalid_login',
                message=_('Enter a valid domain. This value may contain only \
lowercase letters, numbers, and "-" character.'),
            ),
            validate_client_login_restrictions,
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
    city = models.ForeignKey(
        'hotels.City',
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        verbose_name=_('city'),
        db_index=True)
    region = models.ForeignKey(
        'hotels.Region',
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        verbose_name=_('region'),
        db_index=True)
    address = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        db_index=True,
        validators=[MinLengthValidator(2)],
        verbose_name=_('address'))
    postal_code = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        db_index=True,
        validators=[MinLengthValidator(2)])
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
    trial_activated = models.BooleanField(
        default=False, db_index=True, verbose_name=_('trial activated'))
    disabled_at = models.DateTimeField(
        db_index=True, null=True, blank=True, verbose_name=_('disabled at'))
    url = models.URLField(
        db_index=True,
        null=True,
        blank=True,
        verbose_name=_('url'),
        help_text=_('maxibooking url'))
    ip = models.GenericIPAddressField(null=True, blank=True)

    @property
    def text(self):
        return '{name}, ИНН {inn}, \
        {postal_code}, {region}, {city}, {address}'.format(
            name=self.name,
            inn=self.ru.inn,
            postal_code=self.postal_code,
            region=self.city,
            city=self.region,
            address=self.address,
        )

    @property
    def world(self):
        return self

    def services_by_category(self, next=False):
        """
        Grouped client services
        """
        return self.services.get_client_services_by_category(self, next)

    def check_status(self):
        """
        Check client status
        """
        if self.status == 'disabled' and\
           not self.orders.get_expired(('archived',)).count():
            self.status = 'active'
            self.save()

    def get_bill_company(self):
        """
        Get company for bill
        """
        return Company.objects.get_for_bill(self)

    def restrictions_update(self, rooms=None):
        """
        Update client restrictions
        """
        if not rooms:
            rooms = Client.objects.count_rooms(client=self)
        self.restrictions.rooms_limit = rooms
        self.restrictions.save()

    @property
    def language(self):
        return 'ru' if self.country.tld == 'ru' else 'en'

    def __str__(self):
        return '{} - {}'.format(self.login, self.name)

    class Meta:
        ordering = ['-created']


class ClientRu(CountryBase):
    """
    Client ru fields
    """
    passport_serial = models.CharField(
        max_length=4,
        db_index=True,
        validators=[
            MinLengthValidator(4),
            MaxLengthValidator(4),
            integer_validator,
        ],
        verbose_name=_('passport serial'))
    passport_number = models.CharField(
        max_length=6,
        db_index=True,
        validators=[
            MinLengthValidator(6),
            MaxLengthValidator(6),
            integer_validator,
        ],
        verbose_name=_('passport number'))
    passport_date = models.DateTimeField(verbose_name=_('passport date'))
    passport_issued_by = models.CharField(
        max_length=255,
        db_index=True,
        validators=[MinLengthValidator(4)],
        verbose_name=_('passport issued by'))
    inn = models.CharField(
        max_length=13,
        db_index=True,
        validators=[
            MinLengthValidator(10),
            MaxLengthValidator(13),
            integer_validator,
        ],
        verbose_name=_('inn'))
    client = models.OneToOneField(
        Client, on_delete=models.CASCADE, related_name='ru', primary_key=True)


class ClientAuth(CommonInfo, TimeStampedModel):
    """
    Client authentication class
    """
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        db_index=True,
        verbose_name=_('client'),
        related_name='authentications',
    )
    auth_date = models.DateTimeField(
        db_index=True,
        verbose_name=_('authentication date'),
    )
    ip = models.GenericIPAddressField(db_index=True)
    user_agent = models.TextField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name=_('user agent'),
        validators=[MinLengthValidator(2)])

    class Meta:
        ordering = ['auth_date']
        verbose_name_plural = _('Client authentications')


class ClientService(CommonInfo, TimeStampedModel):
    """
    ClientService class
    """
    STATUSES = (
        ('archive', _('archive')),
        ('processing', _('processing')),
        ('active', _('active')),
        ('next', _('next')),
    )

    objects = ClientServiceManager()

    is_enabled = models.BooleanField(
        default=True, db_index=True, verbose_name=_('is enabled'))
    status = models.CharField(
        max_length=20,
        default='active',
        choices=STATUSES,
        verbose_name=_('status'),
        db_index=True)
    is_paid = models.BooleanField(
        default=False, db_index=True, verbose_name=_('is paid'))
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

    @property
    def price_for_unit(self):
        return self.price / self.quantity

    @property
    def group_quantity(self):
        """
        Service quantity for service group
        """
        service = self.service
        return {
            'connection':
            service.default_rooms * self.quantity
            if service.default_rooms else 0,
        }.get(service.type, self.quantity)

    def price_repr(self):
        return '{} {}'.format(
            getattr(self.price, 'amount', ''), self.price.currency)

    price_repr.short_description = _('price')

    def get_default_begin(self, connection=False):
        """
        Get default begin for client_service
        """
        prev = ClientService.objects.get_prev(self)
        default_begin = self.service.get_default_begin()
        begin = default_begin
        if prev:
            begin = prev.end

        return begin if begin >= default_begin else default_begin

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

        if self.status == 'active':
            ClientService.objects.deactivate(
                client=self.client,
                service_type=self.service.type,
                exclude_pk=self.pk)

    @staticmethod
    def validate_dates(begin, end, is_new):
        # if is_new and begin and begin < timezone.now():
        #     raise ValidationError(_('Please correct begin date.'))
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
                status=self.status,
                quantity=self.quantity,
                service__period_units=service.period_units,
                is_enabled=True).exclude(id=self.id).exists():
            raise ValidationError(
                _('Client service with this type already exists.'))

    def __str__(self):
        return '#{} - {} - {} - {}'.format(self.id, self.client, self.service,
                                           self.price)

    class Meta:
        ordering = ['-created']
