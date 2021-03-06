"""
The client admin module
"""
import arrow
import phonenumbers
from ajax_select import make_ajax_form
from ajax_select.admin import AjaxSelectAdmin
from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from django.db.models import Count, Prefetch
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from rangefilter.filter import DateRangeFilter
from reversion.admin import VersionAdmin
from tabbed_admin import TabbedModelAdmin

from billing.admin import (AdminRowActionsMixin, ArchorAdminMixin,
                           ChangeOwnInlineMixin, ChangePermissionInlineMixin,
                           ChangePermissionMixin, DictAdminMixin,
                           ManagerInlineListMixin, ShowAllInlineAdminMixin,
                           TextFieldListFilter)
from billing.models import Comment
from finances.models import ClientDiscount, Order
from hotels.models import Property

from .admin_filters import ClientIsPaidListFilter
from .models import (Client, ClientAuth, ClientRu, ClientService,
                     ClientWebsite, Company, CompanyRu, CompanyWorld,
                     RefusalReason, Restrictions, SalesStatus)
from .tasks import install_client_task


@admin.register(RefusalReason)
class RefusalReasonAdmin(DictAdminMixin, VersionAdmin):
    pass


@admin.register(SalesStatus)
class SalesStatusAdmin(DictAdminMixin, VersionAdmin):
    """
    SalesStatus admin interface
    """

    def get_list_display(self, request):
        parent = super().get_list_display(request)
        parent.insert(2, 'color_html')
        return parent

    def get_fieldsets(self, request, obj=None):
        parent = super().get_fieldsets(request, obj)
        parent[0][1]['fields'].append('color')
        return parent

    def color_html(self, obj):
        template = """
        <span style='background-color: {};' class='color'>&nbsp;</span>
        """
        return mark_safe(template.format(obj.color))

    color_html.short_description = _('color')

    class Media:
        css = {'all': ('css/admin/clients.css', )}


@admin.register(ClientAuth)
class ClientAuthAdmin(VersionAdmin, AjaxSelectAdmin):
    """
    ClientAuth admin interface
    """
    list_display = ('id', 'client', 'auth_date', 'ip', 'user_agent')
    list_display_links = (
        'id',
        'client',
    )
    list_filter = (('auth_date', DateRangeFilter), ('client__login',
                                                    TextFieldListFilter))
    search_fields = ('=pk', 'ip', 'client__name', 'client__email',
                     'client__login', 'user_agent')
    readonly_fields = ('created', 'modified', 'created_by', 'modified_by')
    raw_id_fields = ('client', )
    fieldsets = (
        ('General', {
            'fields': ('client', 'auth_date', 'ip', 'user_agent')
        }),
        ('Options', {
            'fields': ('created', 'modified', 'created_by', 'modified_by')
        }),
    )
    list_select_related = ('client', )
    form = make_ajax_form(ClientService, {
        'client': 'clients',
    })


@admin.register(ClientService)
class ClientServiceAdmin(ChangePermissionMixin, VersionAdmin, AjaxSelectAdmin):
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
                   ('begin', DateRangeFilter), ('end', DateRangeFilter))
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


class ClientServiceInlineAdmin(ChangePermissionInlineMixin,
                               admin.TabularInline):
    """
    ClientServiceInline admin interface
    """
    model = ClientService
    fields = ('service', 'client', 'quantity', 'price_repr', 'begin', 'end',
              'status', 'is_enabled')
    raw_id_fields = ('service', 'client')
    readonly_fields = ('price_repr', )

    show_change_link = True


class PropertyInlineAdmin(ChangePermissionInlineMixin):
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


class CompanyInlineAdmin(ChangePermissionInlineMixin):
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


class ClientAuthInlineAdmin(ShowAllInlineAdminMixin):
    """
    ClientAuthInline admin interface
    """
    model = ClientAuth
    fields = ('auth_date', 'ip', 'user_agent', 'all')
    readonly_fields = fields
    show_change_link = True
    can_delete = False
    max_num = 20
    extra = 1
    verbose_name_plural = "Last logins (3 days)"
    all_url = 'admin:clients_clientauth_changelist'

    def get_queryset(self, request):
        query = super().get_queryset(request)
        date_limit = arrow.utcnow().shift(days=-1).datetime
        return query.filter(auth_date__gte=date_limit)


class OrderInlineAdmin(ShowAllInlineAdminMixin, ManagerInlineListMixin):
    """
    OrderInline admin interface
    """
    model = Order
    fields = ('price_str', 'status', 'expired_date', 'paid_date', 'modified',
              'all')
    readonly_fields = fields
    show_change_link = True
    can_delete = False
    max_num = 20
    extra = 1
    verbose_name_plural = "Last orders (3 months)"
    all_url = 'admin:finances_order_changelist'

    def get_queryset(self, request):
        query = super().get_queryset(request)
        date_limit = arrow.utcnow().shift(months=-3).datetime
        return query.filter(created__gte=date_limit)


class ClientRuAdmin(admin.StackedInline):
    """
    ClientRu admin interface
    """
    model = ClientRu
    readonly_fields = ('created', 'modified', 'created_by', 'modified_by')
    fieldsets = (
        ('Passport', {
            'fields': ('passport_serial', 'passport_number', 'passport_date',
                       'passport_issued_by')
        }),
        ('Finance', {
            'fields': ('inn', )
        }),
        ('Options', {
            'fields': ('created', 'modified', 'created_by', 'modified_by')
        }),
    )


class CommentInlineAdmin(ChangeOwnInlineMixin, GenericTabularInline):
    """
    ClientAuthInline admin interface
    """
    model = Comment
    extra = 1
    readonly_fields = ['modified', 'modified_by']
    fields = ('text', 'type', 'date', 'status')

    def get_form(self):
        return None


class WebsiteInlineAdmin(admin.StackedInline):
    """
    This class represents the administration interface
    for client`s website information.
    """
    model = ClientWebsite
    fields = ('url', 'own_domain_name', 'is_enabled', 'created', 'modified',
              'created_by', 'modified_by')
    readonly_fields = ('created', 'modified', 'created_by', 'modified_by')


class DiscountInlineAdmin(admin.StackedInline):
    """
    This class represents the administration interface
    for client`s website information.
    """
    model = ClientDiscount
    fields = ('title', 'percentage_discount', 'start_date', 'end_date',
              'number_of_uses', 'usage_count', 'code', 'manager', 'department',
              'original_discount', 'created', 'modified', 'created_by',
              'modified_by')
    readonly_fields = ('title', 'code', 'usage_count', 'department', 'manager',
                       'created', 'original_discount', 'modified',
                       'created_by', 'modified_by')


@admin.register(Client)
class ClientAdmin(
        ChangePermissionMixin,
        AdminRowActionsMixin,
        VersionAdmin,
        TabbedModelAdmin,
        ArchorAdminMixin,
):
    """
    Client admin interface
    """
    list_display = ('num', 'login', 'login_alias', 'sales_status_html',
                    'email', 'phone', 'name', 'country', 'city', 'status',
                    'installation', 'url', 'rooms', 'website',
                    'trial_activated', 'logins', 'manager', 'expired_date',
                    'created')
    list_select_related = ('country', 'restrictions', 'city', 'manager',
                           'sales_status', 'website')
    list_display_links = ('id', 'login', 'login_alias')
    list_filter = ('status', 'sales_status', 'source', 'installation',
                   'manager', ('created', DateRangeFilter), 'trial_activated',
                   ClientIsPaidListFilter, 'country', 'website__is_enabled')
    search_fields = ('id', 'login', 'email', 'phone', 'name', 'country__name',
                     'manager__username', 'manager__email',
                     'manager__last_name')
    raw_id_fields = ('country', 'region', 'city')
    readonly_fields = [
        'info', 'timezone', 'disabled_at', 'created', 'modified', 'created_by',
        'modified_by', 'managers_history'
    ]
    tab_client = (
        ('General', {
            'fields':
            ('login', 'login_alias', 'email', 'phone', 'name', 'description')
        }),
        ('Address', {
            'fields':
            ('country', 'region', 'city', 'address', 'postal_code', 'timezone')
        }),
        ('Options', {
            'fields': [
                'status', 'installation', 'trial_activated', 'url',
                'disabled_at', 'ip', 'created', 'modified', 'created_by',
                'modified_by'
            ]
        }),
    )
    tab_properties = (
        RestrictionsInlineAdmin,
        PropertyInlineAdmin,
    )
    tab_payer = (
        ClientRuAdmin,
        CompanyInlineAdmin,
    )
    tab_sales = (
        ('General', {
            'fields': ('info', 'source', 'manager', 'manager_code',
                       'managers_history', 'sales_status', 'refusal_reason')
        }),
        CommentInlineAdmin,
    )
    tab_tariff = (ClientServiceInlineAdmin, )
    tab_auth = (ClientAuthInlineAdmin, )
    tab_orders = (OrderInlineAdmin, )
    tab_website = (WebsiteInlineAdmin, )
    tab_discount = (DiscountInlineAdmin, )
    tabs = (
        ('Client', tab_client),
        ('Properties', tab_properties),
        ('Payer', tab_payer),
        ('Tariff', tab_tariff),
        ('Last logins', tab_auth),
        ('Sales', tab_sales),
        ('Orders', tab_orders),
        ('Website', tab_website),
        ('Discount', tab_discount),
    )

    form = make_ajax_form(Client, {
        'manager': 'users',
    })

    def save_related(self, request, form, formsets, change):
        super(ClientAdmin, self).save_related(request, form, formsets, change)
        client = form.instance
        manager = client.manager
        if manager:
            client.managers_history.add(manager)

    def get_tabs(self, request, obj=None):
        tabs = super().get_tabs(request, obj)
        if request.user.is_superuser:
            return tabs
        fields = tabs[0][1][-1][1]['fields']

        for title in ('created_by', 'modified_by'):
            if title in fields:
                fields.remove(title)

        return tabs

    def get_readonly_fields(self, request, obj=None):
        parent = super().get_readonly_fields(request, obj)
        user = request.user
        if 'manager' not in parent and \
           not user.has_perm('clients.change_client'):
            parent.append('manager')
        return parent

    def get_search_results(self, request, queryset, search_term):

        phone_str = search_term
        if search_term.isnumeric() and len(search_term) > 7:
            phone_str = '+' + search_term

        try:
            phone = phonenumbers.parse(phone_str)
            search_term = phonenumbers.format_number(
                phone, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
        except phonenumbers.phonenumberutil.NumberParseException:
            pass

        queryset, use_distinct = super().get_search_results(
            request, queryset, search_term)
        return queryset, use_distinct

    def info(self, obj):
        return mark_safe('<br>'.join([
            obj.login or '-',
            obj.name or '-',
            obj.email or '-',
            str(obj.phone) if obj.phone else '-',
        ]))

    info.short_description = _('client')

    def sales_status_html(self, obj):
        sales_status = obj.sales_status
        if not sales_status:
            return '-'
        template = """
        <span style='background-color: {}; margin-right: 2px;' \
class='color'>&nbsp;</span><br> {}
        """
        return mark_safe(template.format(sales_status.color, sales_status))

    sales_status_html.short_description = _('sales')

    def save_formset(self, request, form, formset, change):
        def _check(o):
            user = request.user
            if o.pk and isinstance(o, Comment) and o.created_by != user:
                return False
            return True

        instances = formset.save(commit=False)
        for obj in formset.deleted_objects:
            if _check(obj):
                obj.delete()
        for instance in instances:
            if _check(instance):
                instance.save()
        formset.save_m2m()

    def install(self, request, obj):
        """
        Install client
        """
        self.message_user(request, _('Installation successfully started.'))
        install_client_task.delay(client_id=obj.id)

    def set_manager(self, request, obj):
        """
        Set manager from request
        """
        obj.manager = request.user
        obj.save()
        self.message_user(request, _('Client manger successfully saved.'))
        return redirect(
            reverse('admin:clients_client_change', args=[obj.id]) + '#tabs-6')

    def rooms(self, obj):
        """
        Client rooms
        """
        return obj.restrictions.rooms_limit

    def get_row_actions(self, obj):
        row_actions = [
            {
                'label': 'Install',
                'action': 'install',
                'enabled': obj.installation != 'installed',
            },
            {
                'label': 'Manager',
                'action': 'set_manager',
                'enabled': obj.manager is None,
            },
        ]
        row_actions += super(ClientAdmin, self).get_row_actions(obj)
        return row_actions

    def logins(self, obj):
        return obj.auth_count

    @staticmethod
    def expired_date(obj: Client):
        """
        Get the date when the user will be blocked
        """
        order = obj.orders.all().first()
        return getattr(order, 'expired_date', None)

    def get_queryset(self, request):
        query = super().get_queryset(request)
        prefetch = Prefetch('orders',
                            queryset=Order.objects.filter(
                                status='new').order_by('expired_date'))
        query = query.annotate(
            auth_count=Count('authentications')).prefetch_related(prefetch)
        return query

    def render_change_form(self, request, context, *args, **kwargs):
        query = SalesStatus.objects.filter_is_enabled()
        context['adminform'].form.fields['sales_status'].queryset = query
        return super().render_change_form(request, context, *args, **kwargs)

    class Media:
        js = ('js/admin/clients.js', )
        css = {'all': ('css/admin/clients.css', )}


class CompanyWorldAdmin(admin.StackedInline):
    """
    CompanyWorld admin interface
    """
    model = CompanyWorld
    fields = ('swift', 'created', 'modified', 'created_by', 'modified_by')
    readonly_fields = ('created', 'modified', 'created_by', 'modified_by')


class CompanyRuAdmin(admin.StackedInline):
    """
    CompanyRu admin interface
    """
    model = CompanyRu
    readonly_fields = ('created', 'modified', 'created_by', 'modified_by')
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
        ('Options', {
            'fields': ('created', 'modified', 'created_by', 'modified_by')
        }),
    )


@admin.register(Company)
class CompanyAdmin(ChangePermissionMixin, VersionAdmin, AjaxSelectAdmin):
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
