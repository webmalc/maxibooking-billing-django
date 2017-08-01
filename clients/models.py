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

    def __str__(self):
        return '{} - {}'.format(self.login, self.name)

    class Meta:
        ordering = ['-created']


class ClientService(CommonInfo, TimeStampedModel):
    """
    ClientService class
    """
    is_enabled = models.BooleanField(
        default=True, db_index=True, verbose_name=_('is enabled'))
    price = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        verbose_name=_('price'),
        validators=[MinValueValidator(0)],
        db_index=True)
    quantity = models.PositiveIntegerField(
        verbose_name=_('quantity'),
        db_index=True,
        validators=[MinValueValidator(1)])
    start_at = models.DateTimeField(
        db_index=True, verbose_name=_('start date'), auto_now_add=True)
    begin = models.DateTimeField(db_index=True, verbose_name=_('begin date'))
    end = models.DateTimeField(db_index=True, verbose_name=_('end date'))
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

    def save(self, *args, **kwargs):
        self.price = self.service.get_price(client=self.client) * self.quantity
        if self.start_at is None:
            self.start_at = timezone.now()
        super(ClientService, self).save(*args, **kwargs)

    @staticmethod
    def validate_dates(begin, end):
        if begin and end and begin > end:
            raise ValidationError(_('Please correct dates'))

    def clean(self):
        ClientService.validate_dates(self.begin, self.end)

    def __str__(self):
        return '{} - {}'.format(self.client, self.service)

    class Meta:
        ordering = ['-created']
