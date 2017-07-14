from cities_light.abstract_models import (AbstractCity, AbstractCountry,
                                          AbstractRegion)
from cities_light.receivers import connect_default_signals
from django.utils.translation import ugettext_lazy as _


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
