from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from django_admin_row_actions import AdminRowActionsMixin
from reversion.admin import VersionAdmin

from finances.models import Order
from hotels.models import Property

from .models import Client, ClientService
from .tasks import install_client_task


@admin.register(Order)
class OrderAdmin(VersionAdmin):
    """
    Order admin interface
    """
    list_display = ('id', 'price', 'status', 'client', 'expired_date',
                    'paid_date', 'created', 'modified')
    list_display_links = ('id', 'price', )
    list_filter = ('status', 'expired_date', 'paid_date', 'created')
    search_fields = ('id', 'services__service__title',
                     'services__service__description', 'client__name',
                     'client__email', 'client__login')
    readonly_fields = ('created', 'modified', 'paid_date', 'created_by',
                       'modified_by')
    raw_id_fields = ('client', )
    fieldsets = (('General', {
        'fields': ('price', 'client', 'expired_date', 'note')
    }), ('Options', {
        'fields': ('status', 'paid_date', 'created', 'modified', 'created_by',
                   'modified_by')
    }), )
    list_select_related = ('client', )


class OrdersInlineAdmin(admin.TabularInline):
    """
    OrdersInline admin interface
    """
    model = Order.client_services.through
    raw_id_fields = ('order', )
    show_change_link = True
    extra = 1
    verbose_name = 'Order'
    verbose_name_plural = 'Orders'
    max_num = 20


@admin.register(ClientService)
class ClientServiceAdmin(VersionAdmin):
    """
    ClientService admin interface
    """
    list_display = ('id', 'service', 'client', 'quantity', 'price', 'begin',
                    'end', 'status', 'is_enabled')
    list_display_links = ('id', 'service', )
    list_filter = ('service', 'is_enabled', 'begin', 'end')
    search_fields = ('id', 'service__title', 'client__name', 'client__email',
                     'client__login')
    readonly_fields = ('start_at', 'created', 'modified', 'created_by',
                       'modified_by', 'price', 'country')
    raw_id_fields = ('service', 'client', 'country')
    inlines = (OrdersInlineAdmin, )
    fieldsets = (('General', {
        'fields': ('service', 'client', 'quantity', 'price', 'begin', 'end')
    }), ('Options', {
        'fields': ('status', 'is_enabled', 'country', 'start_at', 'created',
                   'modified', 'created_by', 'modified_by')
    }), )
    list_select_related = ('service', 'client')


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
    readonly_fields = ('created', 'modified', 'created_by', 'modified_by',
                       'rooms_limit')
    list_select_related = ('country', )
    fieldsets = (('General', {
        'fields': ('login', 'email', 'phone', 'name', 'description', 'country')
    }), ('Options', {
        'fields': ('status', 'installation', 'rooms_limit', 'created',
                   'modified', 'created_by', 'modified_by')
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
