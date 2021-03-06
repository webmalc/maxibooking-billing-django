import re

from cities_light.abstract_models import (AbstractCity, AbstractCountry,
                                          AbstractRegion)
from cities_light.receivers import connect_default_signals
from django.core.validators import MinLengthValidator, MinValueValidator
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django_extensions.db.models import TimeStampedModel
from djmoney.models.fields import MoneyField
from moneyed import EUR, Money
from timezone_field import TimeZoneField

from billing.models import (CachedModel, CheckedModel, ClientPermissionsModel,
                            CommonInfo, GetManagerMixin)
from finances.lib.calc import CURRENCIES_CODES

from .managers import PropertyManager, RoomManager


class CityMixin(CheckedModel):
    """
    City, Region, County name mixin
    """

    def get_first_cyrilic_alternate_name(self):
        """
        Returns first cyrilic alternate name
        :return: string
        """
        if not self.alternate_names:
            return None

        for name in self.alternate_names.split(','):
            if re.match(r'[А-яа-я\-\s]{2,}', name):
                return name
        return None

    get_first_cyrilic_alternate_name.short_description = 'Cyrilic name'
    get_first_cyrilic_alternate_name.admin_order_field = 'cyrilic_names'

    def __str__(self):
        return self.name


class Country(CachedModel, CityMixin, AbstractCountry):
    """ HH country model."""

    is_enabled = models.BooleanField(
        default=True, db_index=True, verbose_name=_('is enabled'))

    is_checked = models.BooleanField(
        default=True, db_index=True, verbose_name=_('is checked'))

    is_former = models.BooleanField(
        default=False, db_index=True, verbose_name=_('is former'))

    currency = models.CharField(
        max_length=3,
        choices=zip(CURRENCIES_CODES, CURRENCIES_CODES),
        null=True,
        blank=True,
    )

    request_client = models.ForeignKey(
        'clients.Client',
        on_delete=models.SET_NULL,
        related_name="%(app_label)s_%(class)s_request_client_by",
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ['name']
        verbose_name_plural = _('countries')


connect_default_signals(Country)


class Region(CachedModel, CityMixin, AbstractRegion):
    """ HH region model."""

    is_enabled = models.BooleanField(
        default=True, db_index=True, verbose_name=_('is enabled'))

    is_checked = models.BooleanField(
        default=True, db_index=True, verbose_name=_('is checked'))

    request_client = models.ForeignKey(
        'clients.Client',
        on_delete=models.SET_NULL,
        related_name="%(app_label)s_%(class)s_request_client_by",
        null=True,
        blank=True,
    )

    def get_display_name(self):
        return '%s, %s' % (self, self)

    class Meta:
        ordering = ['name']


connect_default_signals(Region)


class City(CachedModel, CityMixin, AbstractCity):
    """ HH city model."""

    is_enabled = models.BooleanField(
        default=True, db_index=True, verbose_name=_('is enabled'))

    is_checked = models.BooleanField(
        default=True, db_index=True, verbose_name=_('is checked'))

    request_client = models.ForeignKey(
        'clients.Client',
        on_delete=models.SET_NULL,
        related_name="%(app_label)s_%(class)s_request_client_by",
        null=True,
        blank=True,
    )
    timezone = TimeZoneField(null=True, blank=True)

    @property
    def full_name(self):
        return self.get_display_name()

    def get_display_name(self):
        if self.region_id:
            return '%s, %s, %s' % (self.name, self.region, self.country)
        else:
            return '%s, %s' % (self.name, self.country)

    class Meta:
        ordering = ['name']
        unique_together = (('region', 'name'), ('region', 'slug'))
        verbose_name_plural = _('cities')


connect_default_signals(City)


class Property(CommonInfo, TimeStampedModel, ClientPermissionsModel,
               GetManagerMixin):
    """
    Property class
    """
    TYPES = (('hotel', _('Hotel')), ('hostel', _('Hostel')),
             ('flat', _('Flat')), ('b&b', _('B&B')), ('vacation_rental',
                                                      _('Vacation rental')))

    objects = PropertyManager()

    name = models.CharField(
        max_length=255,
        verbose_name=_('name'),
        db_index=True,
        validators=[MinLengthValidator(2)])
    description = models.TextField(
        null=True,
        blank=True,
        verbose_name=_('description'),
        db_index=True,
        validators=[MinLengthValidator(2)])
    address = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('address'),
        db_index=True,
        validators=[MinLengthValidator(2)])
    city = models.ForeignKey(
        City,
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        verbose_name=_('city'),
        db_index=True,
    )
    type = models.CharField(
        max_length=20,
        default='hotel',
        choices=TYPES,
        verbose_name=_('type'),
        db_index=True)
    url = models.URLField(
        blank=True, null=True, db_index=True, verbose_name=_('url'))
    client = models.ForeignKey(
        'clients.Client',
        on_delete=models.CASCADE,
        verbose_name=_('client'),
        db_index=True,
        related_name='properties')

    @property
    def rooms_count(self):
        return self.rooms.count_rooms(self.client)

    class Meta(ClientPermissionsModel.Meta):
        ordering = ['name']
        verbose_name_plural = 'properties'


class Room(CommonInfo, TimeStampedModel):
    """
    Room class
    """
    objects = RoomManager()

    name = models.CharField(
        max_length=255,
        verbose_name=_('name'),
        db_index=True,
        validators=[MinLengthValidator(2)])
    description = models.TextField(
        null=True,
        blank=True,
        verbose_name=_('description'),
        db_index=True,
        validators=[MinLengthValidator(2)])
    rooms = models.PositiveIntegerField(
        verbose_name=_('rooms'),
        db_index=True,
        validators=[MinValueValidator(1)],
        help_text=_('max rooms'))
    max_occupancy = models.PositiveIntegerField(
        verbose_name=_('max occupancy'),
        db_index=True,
        validators=[MinValueValidator(1)],
        default=1,
        help_text=_('max guest occupancy'))
    price = MoneyField(
        max_digits=20,
        decimal_places=2,
        verbose_name=_('price'),
        default=Money(0, EUR),
        db_index=True)
    property = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        verbose_name=_('property'),
        db_index=True,
        related_name='rooms')

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'rooms'
