from ajax_select import make_ajax_form
from ajax_select.admin import AjaxSelectAdmin
from django.contrib import admin
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django_admin_row_actions import AdminRowActionsMixin
from reversion.admin import VersionAdmin

from billing.admin import TextFieldListFilter
from hotels.models import Property

from .models import (Client, ClientRu, ClientService, Company, CompanyRu,
                     CompanyWorld, Restrictions)
from .tasks import install_client_task


@admin.register(ClientService)
class ClientServiceAdmin(VersionAdmin, AjaxSelectAdmin):
    """
    ClientService admin interface
    """
    list_display = ('id', 'service', 'client', 'quantity', 'price', 'begin',
                    'end', 'status', 'is_enabled', 'is_paid')
    list_display_links = (
        'id',
        'service',
    )
    list_filter = ('service', 'is_enabled', ('orders', TextFieldListFilter),
                   'begin', 'end')
    search_fields = ('=pk', '=orders__pk', 'service__title', 'client__name',
                     'client__email', 'client__login')
    readonly_fields = ('start_at', 'created', 'price_repr', 'modified',
                       'created_by', 'modified_by', 'country')
    raw_id_fields = ('service', 'client', 'country', 'orders')
    fieldsets = (
        ('General', {
            'fields': ('service', 'client', 'quantity', 'price_repr', 'begin',
                       'end', 'orders')
        }),
        ('Options', {
            'fields':
            ('status', 'is_enabled', 'is_paid', 'country', 'start_at',
             'created', 'modified', 'created_by', 'modified_by')
        }),
    )
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
    fields = ('service', 'client', 'quantity', 'price_repr', 'begin', 'end',
              'status', 'is_enabled')
    raw_id_fields = ('service', 'client')
    readonly_fields = ('price_repr', )

    show_change_link = True


class PropertyInlineAdmin(admin.TabularInline):
    """
    PropertyInline admin interface
    """
    model = Property
    fields = ('name', 'type', 'city')
    raw_id_fields = ('city', )
    show_change_link = True


class RestrictionsInlineAdmin(admin.StackedInline):
    """
    RestrictionsInline admin interface
    """
    model = Restrictions
    fields = ('rooms_limit', )
    can_delete = False


class CompanyInlineAdmin(admin.TabularInline):
    """
    CompanyInline admin interface
    """
    model = Company
    fields = (
        'name',
        'bank',
    )
    readonly_fields = fields
    show_change_link = True
    can_delete = False

    def has_add_permission(self, *args, **kwargs):
        return False


class ClientRuAdmin(admin.StackedInline):
    """
    ClientRu admin interface
    """
    model = ClientRu
    fieldsets = (
        ('Passport', {
            'fields': ('passport_serial', 'passport_number', 'passport_date',
                       'passport_issued_by')
        }),
        ('Finance', {
            'fields': ('inn', )
        }),
    )


@admin.register(Client)
class ClientAdmin(AdminRowActionsMixin, VersionAdmin):
    """
    Client admin interface
    """
    list_display = ('id', 'login', 'email', 'phone', 'name', 'status',
                    'trial_activated', 'created')
    list_display_links = ('id', 'login')
    list_filter = ('status', 'installation', 'trial_activated', 'country')
    search_fields = ('id', 'login', 'email', 'phone', 'name', 'country__name')
    raw_id_fields = ('country', 'region', 'city')
    readonly_fields = ('disabled_at', 'created', 'modified', 'created_by',
                       'modified_by')
    list_select_related = ('country', )
    fieldsets = (
        ('General', {
            'fields': ('login', 'email', 'phone', 'name', 'description')
        }),
        ('Address', {
            'fields': ('country', 'region', 'city', 'address', 'postal_code')
        }),
        ('Options', {
            'fields':
            ('status', 'installation', 'trial_activated', 'url', 'disabled_at',
             'ip', 'created', 'modified', 'created_by', 'modified_by')
        }),
    )
    inlines = (
        ClientRuAdmin,
        RestrictionsInlineAdmin,
        PropertyInlineAdmin,
        ClientServiceInlineAdmin,
        CompanyInlineAdmin,
    )

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


class CompanyWorldAdmin(admin.StackedInline):
    """
    CompanyWorld admin interface
    """
    model = CompanyWorld
    fields = ('swift', )


class CompanyRuAdmin(admin.StackedInline):
    """
    CompanyRu admin interface
    """
    model = CompanyRu
    fieldsets = (
        ('General', {
            'fields': ('form', 'ogrn', 'inn', 'kpp')
        }),
        ('Bank', {
            'fields': ('bik', 'corr_account')
        }),
        ('Boss', {
            'fields': ('boss_firstname', 'boss_lastname', 'boss_patronymic',
                       'boss_operation_base', 'proxy_number', 'proxy_date')
        }),
    )


@admin.register(Company)
class CompanyAdmin(VersionAdmin, AjaxSelectAdmin):
    """
    Company admin interface
    """
    list_display = ('id', 'name', 'client', 'bank', 'created')
    list_display_links = ('id', 'name')
    list_filter = (('client', TextFieldListFilter), )
    search_fields = ('id', 'client__login', 'client__email', 'client__name',
                     'name', 'ru__boss_lastname', 'ru__ogrn', 'ru__inn',
                     'ru__kpp', 'account_number', 'ru__bik', 'world__swift')
    raw_id_fields = ('city', 'region', 'client')
    readonly_fields = ('created', 'modified', 'created_by', 'modified_by')
    list_select_related = ('client', )
    form = make_ajax_form(Company, {
        'client': 'clients',
    })
    inlines = (CompanyWorldAdmin, CompanyRuAdmin)
    fieldsets = (
        ('General', {
            'fields': ('client', 'name')
        }),
        ('Address', {
            'fields': ('region', 'city', 'address', 'postal_code')
        }),
        ('Bank', {
            'fields': ('account_number', 'bank')
        }),
        ('Options', {
            'fields': ('created', 'modified', 'created_by', 'modified_by')
        }),
    )
