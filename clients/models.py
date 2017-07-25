from django.core.validators import (MinLengthValidator, MinValueValidator,
                                    RegexValidator)
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django_extensions.db.models import TimeStampedModel
from phonenumber_field.modelfields import PhoneNumberField

from billing.models import CommonInfo
from finances.models import Service


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
        validators=[
            MinLengthValidator(4), RegexValidator(
                regex='^[a-z0-9\-]*$',
                code='invalid_login',
                message=_('Enter a valid login. This value may contain only \
lowercase letters, numbers, and "-" character.'))
        ])
    email = models.EmailField(
        db_index=True, unique=True, verbose_name=_('e-mail'))
    phone = PhoneNumberField(max_length=50, db_index=True)
    name = models.CharField(
        max_length=255, db_index=True, validators=[MinLengthValidator(2)])
    description = models.TextField(
        null=True,
        blank=True,
        db_index=True,
        validators=[MinLengthValidator(2)])
    status = models.CharField(
        max_length=20,
        default='not_confirmed',
        choices=STATUSES,
        db_index=True)
    installation = models.CharField(
        max_length=20,
        default='not_installed',
        choices=INSTALLATION,
        db_index=True)

    def __str__(self):
        return '{} - {}'.format(self.login, self.name)

    class Meta:
        ordering = ['-created']


class ClientServices(CommonInfo, TimeStampedModel):
    """
    ClientServices class
    """
    is_enabled = models.BooleanField(default=True, db_index=True)
    price = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        db_index=True)
    quantity = models.PositiveIntegerField(db_index=True)
    begin = models.DateTimeField(db_index=True, verbose_name=_('start date'))
    end = models.DateTimeField(db_index=True, verbose_name=_('end date'))
    service = models.ForeignKey(
        Service,
        on_delete=models.PROTECT,
        db_index=True,
        related_name='client_services')
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        db_index=True,
        related_name='services')

    def __str__(self):
        return '{} - {}'.format(self.client, self.service)

    class Meta:
        ordering = ['-created']
