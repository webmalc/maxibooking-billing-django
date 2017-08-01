from django.contrib import admin
from modeltranslation.admin import TabbedExternalJqueryTranslationAdmin
from reversion.admin import VersionAdmin

from .models import Price, Service


class PriceInlineAdmin(admin.TabularInline):
    """
    Price admin interface
    """
    model = Price
    fields = ('price', 'country', 'is_enabled', 'created', 'modified',
              'created_by', 'modified_by')
    raw_id_fields = ('country', )
    readonly_fields = ('created', 'modified', 'created_by', 'modified_by')


@admin.register(Service)
class ServiceAdmin(VersionAdmin, TabbedExternalJqueryTranslationAdmin):
    """
    Service admin interface
    """
    list_display = ('id', 'title', 'period', 'period_units', 'is_enabled',
                    'created')
    list_display_links = ('id', 'title')
    list_filter = ('is_enabled', 'period_units', 'created')
    search_fields = ('title', 'description', 'price', 'id')
    readonly_fields = ('created', 'modified', 'created_by', 'modified_by',
                       'period_days', 'price')
    inlines = (PriceInlineAdmin, )
    fieldsets = (('General', {
        'fields': ('title', 'description', 'price')
    }), ('Options', {
        'fields': ('period', 'period_units', 'period_days', 'is_enabled',
                   'created', 'modified', 'created_by', 'modified_by')
    }), )
