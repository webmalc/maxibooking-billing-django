from django.core.exceptions import ValidationError
from django.core.validators import (MinLengthValidator, MinValueValidator,
                                    RegexValidator)
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django_extensions.db.models import TimeStampedModel
from phonenumber_field.modelfields import PhoneNumberField

from billing.models import CommonInfo
from hotels.models import Country

from .managers import ClientServiceManager


class Client(CommonInfo, TimeStampedModel):
    """
    Client class
    """
    STATUSES = (('not_confirmed', _('not confirmed')), ('active', _('active')),
                ('disabled', _('disabled')), ('archived', _('archived')))

    INSTALLATION = (('not_installed', _('not installed')),
                    ('process', _('process')), ('installed', _('installed')))

    login = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        verbose_name=_('login'),
        validators=[
            MinLengthValidator(4), RegexValidator(
                regex='^[a-z0-9\-]*$',
                code='invalid_login',
                message=_('Enter a valid login. This value may contain only \
lowercase letters, numbers, and "-" character.'))
        ])
    email = models.EmailField(
        db_index=True, unique=True, verbose_name=_('e-mail'))
    phone = PhoneNumberField(
        max_length=50, db_index=True, verbose_name=_('phone'))
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

    @property
    def rooms_limit(self):
        """
        Client rooms limit
        """
        return sum([
            s.quantity for s in self.services.all()
            if s.is_enabled and s.service.type == 'rooms'
        ])

    def __str__(self):
        return '{} - {}'.format(self.login, self.name)

    class Meta:
        ordering = ['-created']


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
    price = models.DecimalField(
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
    orders = models.ManyToManyField('finances.Order', verbose_name=_('orders'))

    def save(self, *args, **kwargs):
        self.price = self.service.get_price(client=self.client) * self.quantity

        if self.begin is None:
            self.begin = self.service.get_default_begin()
        if self.end is None:
            self.end = self.service.get_default_end(self.begin)
        if self.country_id is None:
            self.country = self.client.country
        if self.start_at is None:
            self.start_at = timezone.now()
        super(ClientService, self).save(*args, **kwargs)

    @staticmethod
    def validate_dates(begin, end):
        if begin and end and begin > end:
            raise ValidationError(_('Please correct dates.'))

    @staticmethod
    def validate_service(service, client):
        if service and not service.get_price(client=client):
            raise ValidationError(_('Empty service prices.'))

    def clean(self):
        ClientService.validate_dates(self.begin, self.end)
        ClientService.validate_service(self.service, self.client)

    def validate_unique(self, exclude=None):
        super(ClientService, self).validate_unique(exclude)
        service_type = self.service.type
        if service_type != 'other' and ClientService.objects.filter(
                client=self.client, service__type=service_type,
                is_enabled=True).exclude(id=self.id).exists():
            raise ValidationError(
                _('Client service with this type already exists.'))

    def __str__(self):
        return '#{} - {} - {}'.format(self.id, self.client, self.service)

    class Meta:
        ordering = ['-created']
        unique_together = (('client', 'is_enabled', 'service'), )
