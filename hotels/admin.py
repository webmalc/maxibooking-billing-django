from django.contrib import admin
from reversion.admin import VersionAdmin

from .models import Property


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
