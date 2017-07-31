from cities_light.admin import CityAdmin as BaseCityAdmin
from cities_light.admin import CountryAdmin as BaseCountryAdmin
from cities_light.admin import RegionAdmin as BaseRegionAdmin
from django.contrib import admin
from modeltranslation.admin import TabbedExternalJqueryTranslationAdmin
from reversion.admin import VersionAdmin

from .models import City, Country, Property, Region


@admin.register(Property)
class PropertyAdmin(VersionAdmin):
    """
    Property admin interface
    """
    list_display = ('id', 'name', 'type', 'city', 'client', 'created')
    list_display_links = ('id', 'name')
    list_filter = ('type', 'created_by')
    search_fields = ('id', 'name', 'city__name', 'city__alternate_names',
                     'description', 'client__login', 'client__name',
                     'client__email')
    raw_id_fields = ('city', 'client')
    readonly_fields = ('created', 'modified', 'created_by', 'modified_by')
    fieldsets = (('General', {
        'fields': ('client', 'name', 'description', 'type')
    }), ('Location', {
        'fields': ('city', 'address', 'url')
    }), ('Options', {
        'fields': ('created', 'modified', 'created_by', 'modified_by')
    }), )
    list_select_related = ('city', 'client')


admin.site.unregister(Country)


@admin.register(Country)
class CountryAdmin(BaseCountryAdmin, VersionAdmin,
                   TabbedExternalJqueryTranslationAdmin):
    """
    Country admin interface
    """

    list_display = ['id'] + list(BaseCountryAdmin.list_display)
    list_display_links = ('id', 'name')


admin.site.unregister(Region)


@admin.register(Region)
class RegionAdmin(BaseRegionAdmin, VersionAdmin,
                  TabbedExternalJqueryTranslationAdmin):
    """
    Region admin interface
    """

    list_display = ['id'] + list(BaseRegionAdmin.list_display)
    list_display_links = ('id', 'name')


admin.site.unregister(City)


@admin.register(City)
class CityAdmin(BaseCityAdmin, VersionAdmin,
                TabbedExternalJqueryTranslationAdmin):
    """
    City admin interface
    """

    list_display = ['id'] + list(BaseRegionAdmin.list_display)
    list_display_links = ('id', 'name')
