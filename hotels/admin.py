from django.contrib import admin
from reversion.admin import VersionAdmin

from .models import Property


@admin.register(Property)
class PropertyAdmin(VersionAdmin):
    """
    Property admin interface
    """
    list_display = ('id', 'name', 'type', 'city', 'created', 'created_by')
    list_display_links = ('id', 'name')
    list_filter = ('type', 'created_by')
    search_fields = ('id', 'name', 'city__name', 'city__alternate_names',
                     'description')
    raw_id_fields = ['city']
    readonly_fields = ('created', 'modified', 'created_by', 'modified_by')
    fieldsets = (('General', {
        'fields': ('name', 'description', 'type')
    }), ('Location', {
        'fields': ('city', 'address', 'url')
    }), ('Options', {
        'fields': ('created', 'modified', 'created_by', 'modified_by')
    }), )
