from ajax_select import make_ajax_form
from ajax_select.admin import AjaxSelectAdmin
from django.contrib import admin
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django_admin_row_actions import AdminRowActionsMixin
from reversion.admin import VersionAdmin

from billing.admin import TextFieldListFilter
from hotels.models import Property

from .models import Client, ClientService
from .tasks import install_client_task


@admin.register(ClientService)
class ClientServiceAdmin(VersionAdmin, AjaxSelectAdmin):
    """
    ClientService admin interface
    """
    list_display = ('id', 'service', 'client', 'quantity', 'price', 'begin',
                    'end', 'status', 'is_enabled')
    list_display_links = ('id', 'service', )
    list_filter = ('service', 'is_enabled', ('orders', TextFieldListFilter),
                   'begin', 'end')
    search_fields = ('=pk', '=orders__pk', 'service__title', 'client__name',
                     'client__email', 'client__login')
    readonly_fields = ('start_at', 'created', 'modified', 'created_by',
                       'modified_by', 'price', 'country')
    raw_id_fields = ('service', 'client', 'country', 'orders')
    fieldsets = (('General', {
        'fields':
        ('service', 'client', 'quantity', 'price', 'begin', 'end', 'orders')
    }), ('Options', {
        'fields': ('status', 'is_enabled', 'country', 'start_at', 'created',
                   'modified', 'created_by', 'modified_by')
    }), )
    list_select_related = ('service', 'client')
    form = make_ajax_form(ClientService, {
        'client': 'clients',
        'service': 'services',
    })

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if not obj:
            return form
        form.base_fields['orders'].help_text = """
        <a href="{}?client_services__exact={}" target="_blank">Orders list</a>
        """.format(reverse('admin:finances_order_changelist'), obj.pk)
        return form


class ClientServiceInlineAdmin(admin.TabularInline):
    """
    ClientServiceInline admin interface
    """
    model = ClientService
    fields = ('service', 'client', 'quantity', 'price', 'begin', 'end',
              'status')
    raw_id_fields = ('service', 'client')
    readonly_fields = ('price', )
    show_change_link = True


class PropertyInlineAdmin(admin.TabularInline):
    """
    PropertyInline admin interface
    """
    model = Property
    fields = ('name', 'type', 'city', 'rooms')
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
    readonly_fields = ('disabled_at', 'created', 'modified', 'created_by',
                       'modified_by', 'rooms_limit')
    list_select_related = ('country', )
    fieldsets = (('General', {
        'fields': ('login', 'email', 'phone', 'name', 'description', 'country')
    }), ('Options', {
        'fields': ('status', 'installation', 'rooms_limit', 'disabled_at',
                   'created', 'modified', 'created_by', 'modified_by')
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
