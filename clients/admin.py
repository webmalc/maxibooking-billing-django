from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from django_admin_row_actions import AdminRowActionsMixin
from hotels.models import Property
from reversion.admin import VersionAdmin

from .models import Client, ClientService
from .tasks import install_client_task


@admin.register(ClientService)
class ClientServiceAdmin(VersionAdmin):
    """
    ClientService admin interface
    """
    list_display = ('id', 'service', 'client', 'quantity', 'price', 'begin',
                    'end', 'is_enabled')
    list_display_links = ('id', )
    list_filter = ('service', 'is_enabled', 'begin', 'end')
    search_fields = ('id', 'service__title', 'client__name', 'client__email',
                     'client__login')
    readonly_fields = ('start_at', 'created', 'modified', 'created_by',
                       'modified_by', 'price', 'country')
    raw_id_fields = ('service', 'client', 'country')
    fieldsets = (('General', {
        'fields': ('service', 'client', 'quantity', 'price', 'begin', 'end')
    }), ('Options', {
        'fields': ('is_enabled', 'country', 'start_at', 'created', 'modified',
                   'created_by', 'modified_by')
    }), )
    list_select_related = ('service', 'client')


class ClientServiceInlineAdmin(admin.TabularInline):
    """
    ClientServiceInline admin interface
    """
    model = ClientService
    fields = ('service', 'client', 'quantity', 'price', 'begin', 'end')
    raw_id_fields = ('service', 'client')
    readonly_fields = ('price', )
    show_change_link = True


class PropertyInlineAdmin(admin.TabularInline):
    """
    PropertyInline admin interface
    """
    model = Property
    fields = ('name', 'type', 'city')
    raw_id_fields = ('city', )
    show_change_link = True


@admin.register(Client)
class ClientAdmin(AdminRowActionsMixin, VersionAdmin):
    """
    Client admin interface
    """
    list_display = ('id', 'login', 'email', 'phone', 'name', 'status',
                    'created')
    list_display_links = ('id', 'login')
    list_filter = ('status', 'installation', 'country')
    search_fields = ('id', 'login', 'email', 'phone', 'name', 'country__name')
    raw_id_fields = ('country', )
    readonly_fields = ('created', 'modified', 'created_by', 'modified_by')
    list_select_related = ('country', )
    fieldsets = (('General', {
        'fields': ('login', 'email', 'phone', 'name', 'description', 'country')
    }), ('Options', {
        'fields': ('status', 'installation', 'created', 'modified',
                   'created_by', 'modified_by')
    }), )
    inlines = (PropertyInlineAdmin, ClientServiceInlineAdmin)

    def install(self, request, obj):
        """
        Install client
        """
        self.message_user(request, _('Installation successfully started.'))
        install_client_task.delay(client_id=obj.id)

    def get_row_actions(self, obj):
        row_actions = [
            {
                'label': 'Install',
                'action': 'install',
            },
        ]
        row_actions += super(ClientAdmin, self).get_row_actions(obj)
        return row_actions

    class Media:
        js = ('js/admin/clients.js', )
        css = {'all': ('css/admin/clients.css', )}
