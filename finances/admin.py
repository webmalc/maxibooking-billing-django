from django.contrib import admin
from reversion.admin import VersionAdmin

from .models import Service


@admin.register(Service)
class ClientAdmin(VersionAdmin):
    """
    Service admin interface
    """
    list_display = ('id', 'title', 'price', 'period', 'period_units',
                    'is_enabled', 'created')
    list_display_links = ('id', 'title')
    list_filter = ('is_enabled', 'period_units', 'created')
    search_fields = ('title', 'description', 'price', 'id')
    readonly_fields = ('created', 'modified', 'created_by', 'modified_by',
                       'period_days')
    fieldsets = (('General', {
        'fields': ('title', 'description', 'price')
    }), ('Options', {
        'fields': ('period', 'period_units', 'period_days', 'is_enabled',
                   'created', 'modified', 'created_by', 'modified_by')
    }), )
