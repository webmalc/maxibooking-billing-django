from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from django_admin_row_actions import AdminRowActionsMixin
from reversion.admin import VersionAdmin

from hotels.models import Property

from .models import Client
from .tasks import install_client_task


class PropertyInlineAdmin(admin.TabularInline):
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
    list_filter = ('status', 'installation')
    search_fields = ('id', 'login', 'email', 'phone', 'name')
    readonly_fields = ('created', 'modified', 'created_by', 'modified_by')
    fieldsets = (('General', {
        'fields': ('login', 'email', 'phone', 'name', 'description')
    }), ('Options', {
        'fields': ('status', 'installation', 'created', 'modified',
                   'created_by', 'modified_by')
    }), )
    inlines = (PropertyInlineAdmin, )

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
