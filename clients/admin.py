from django.contrib import admin
from reversion.admin import VersionAdmin

from .models import Client


@admin.register(Client)
class ClientAdmin(VersionAdmin):
    """
    Client admin interface
    """
    list_display = ('id', 'login', 'email', 'phone', 'name', 'status',
                    'created')
    list_display_links = ('id', 'login')
    list_filter = ('status', )
    search_fields = ('id', 'login', 'email', 'phone', 'name')
    readonly_fields = ('created', 'modified', 'created_by', 'modified_by')
    fieldsets = (('General', {
        'fields': ('login', 'email', 'phone', 'name', 'description')
    }), ('Options', {
        'fields':
        ('status', 'created', 'modified', 'created_by', 'modified_by')
    }), )

    class Media:
        js = ('js/admin/clients.js', )
        css = {'all': ('css/admin/clients.css', )}
