from django.core.validators import MinLengthValidator
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django_extensions.db.models import TimeStampedModel
from phonenumber_field.modelfields import PhoneNumberField

from billing.models import CommonInfo


class Client(CommonInfo, TimeStampedModel):
    """
    Client class
    """
    STATUSES = (('not_confirmed', _('not confirmed')), ('active', _('active')),
                ('disabled', _('disabled')), ('archived', _('archived')))

    login = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        validators=[MinLengthValidator(4)])
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

    class Meta:
        ordering = ['-created']
