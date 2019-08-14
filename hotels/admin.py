from cities_light.admin import CityAdmin as BaseCityAdmin
from cities_light.admin import CountryAdmin as BaseCountryAdmin
from cities_light.admin import RegionAdmin as BaseRegionAdmin
from django.contrib import admin
from modeltranslation.admin import TabbedExternalJqueryTranslationAdmin
from reversion.admin import VersionAdmin

from billing.admin import ChangePermissionMixin

from .models import City, Country, Property, Region, Room


class RoomsInlineAdmin(admin.TabularInline):
    """
    ClientServiceInline admin interface
    """
    model = Room
    fields = ('name', 'rooms', 'max_occupancy', 'price', 'description')


@admin.register(Property)
class PropertyAdmin(ChangePermissionMixin, VersionAdmin):
    """
    Property admin interface
    """
    list_display = ('id', 'name', 'type', 'city', 'client', 'created')
    list_display_links = ('id', 'name')
    list_filter = (
        'type',
        'created_by',
    )
    search_fields = ('id', 'name', 'city__name', 'city__alternate_names',
                     'description', 'client__login', 'client__name',
                     'client__email')
    raw_id_fields = ('city', 'client')
    readonly_fields = ('created', 'modified', 'created_by', 'modified_by',
                       'rooms_count')
    inlines = (RoomsInlineAdmin, )
    fieldsets = (
        ('General', {
            'fields': ('client', 'name', 'description', 'type', 'rooms_count')
        }),
        ('Location', {
            'fields': ('city', 'address', 'url')
        }),
        ('Options', {
            'fields': ('created', 'modified', 'created_by', 'modified_by')
        }),
    )
    list_select_related = ('city', 'client')


admin.site.unregister(Country)


class CityAdminMixin(admin.ModelAdmin):
    """
    Base Country, Region, City admin
    """

    list_display_links = ('id', 'name')

    # raw_id_fields = ('request_client', )

    def get_list_display(self, request):
        return ['id'] + list(
            super().get_list_display(request)) + ['is_enabled', 'is_checked']

    def get_list_filter(self, request):
        return list(
            super().get_list_filter(request)) + ['is_enabled', 'is_checked']


@admin.register(Country)
class CountryAdmin(BaseCountryAdmin, VersionAdmin,
                   TabbedExternalJqueryTranslationAdmin, CityAdminMixin):
    """
    Country admin interface
    """
    pass


admin.site.unregister(Region)


@admin.register(Region)
class RegionAdmin(BaseRegionAdmin, VersionAdmin,
                  TabbedExternalJqueryTranslationAdmin, CityAdminMixin):
    """
    Region admin interface
    """
    pass


admin.site.unregister(City)


@admin.register(City)
class CityAdmin(BaseCityAdmin, VersionAdmin,
                TabbedExternalJqueryTranslationAdmin, CityAdminMixin):
    """
    City admin interface
    """
    list_select_related = ('region', 'country')
