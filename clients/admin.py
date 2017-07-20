from django.contrib import admin
from reversion.admin import VersionAdmin

from hotels.models import Property

from .models import Client


class PropertyInlineAdmin(admin.TabularInline):
    model = Property
    fields = ('name', 'type', 'city')
    raw_id_fields = ('city', )
    show_change_link = True


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
    readonly_fields = ('installation', 'created', 'modified', 'created_by',
                       'modified_by')
    fieldsets = (('General', {
        'fields': ('login', 'email', 'phone', 'name', 'description')
    }), ('Options', {
        'fields': ('status', 'installation', 'created', 'modified',
                   'created_by', 'modified_by')
    }), )
    inlines = (PropertyInlineAdmin, )

    class Media:
        js = ('js/admin/clients.js', )
        css = {'all': ('css/admin/clients.css', )}
