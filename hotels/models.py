from cities_light.abstract_models import (AbstractCity, AbstractCountry,
                                          AbstractRegion)
from cities_light.receivers import connect_default_signals
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django_extensions.db.models import TimeStampedModel

from billing.models import CommonInfo


class CityMixin:
    """
    City, Region, County name mixin
    """

    def get_first_alternate_name(self):
        """
        Returns first alternate name
        :return: string
        """
        return self.alternate_names.split(',')[0]

    get_first_alternate_name.short_description = 'Alternative name'
    get_first_alternate_name.admin_order_field = 'alternate_names'

    def __str__(self):
        return self.name


class Country(CityMixin, AbstractCountry):
    """ HH country model."""

    class Meta:
        ordering = ['name']
        verbose_name_plural = _('countries')


connect_default_signals(Country)


class Region(CityMixin, AbstractRegion):
    """ HH region model."""

    def get_display_name(self):
        return '%s, %s' % (self, self)


connect_default_signals(Region)


class City(CityMixin, AbstractCity):
    """ HH city model."""

    def get_display_name(self):
        if self.region_id:
            return '%s, %s, %s' % (self, self.region, self.country)
        else:
            return '%s, %s' % (self.name, self.country)

    class Meta:
        ordering = ['name']
        unique_together = (('region', 'name'), ('region', 'slug'))
        verbose_name_plural = _('cities')


connect_default_signals(City)


class Property(CommonInfo, TimeStampedModel):
    """
    Property class
    """
    TYPES = (('hotel', _('Hotel')), ('hostel', _('Hostel')),
             ('flat', _('Flat')), ('b&b', _('B&B')),
             ('vacation_rental', _('Vacation rental')))

    name = models.CharField(
        max_length=255, verbose_name=_('name'), db_index=True)
    description = models.TextField(
        null=True, blank=True, verbose_name=_('description'), db_index=True)
    address = models.TextField(verbose_name=_('address'), db_index=True)
    city = models.ForeignKey(
        City, on_delete=models.PROTECT, verbose_name=_('city'))
    type = models.CharField(
        max_length=20,
        default='hotel',
        choices=TYPES,
        verbose_name=_('type'),
        db_index=True)
    url = models.URLField(blank=True, null=True, db_index=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'properties'
