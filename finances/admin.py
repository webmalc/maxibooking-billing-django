import jsonpickle
from ajax_select import make_ajax_form
from ajax_select.admin import AjaxSelectAdmin
from django.contrib import admin
from django.http import HttpResponse
from django.utils.translation import ugettext_lazy as _
from django_admin_row_actions import AdminRowActionsMixin
from modeltranslation.admin import TabbedExternalJqueryTranslationAdmin
from rangefilter.filter import DateRangeFilter
from reversion.admin import VersionAdmin

from billing.admin import JsonAdmin, ManagerListMixin, TextFieldListFilter
from finances.systems.lib import BraintreeGateway

from .models import (Discount, Order, Price, Service, ServiceCategory,
                     Subscription, Transaction)
from .systems import manager


@admin.register(Discount)
class DiscountAdmin(AdminRowActionsMixin, VersionAdmin, AjaxSelectAdmin):
    """
    The discount admin interface
    """
    user = None

    list_display = ('id', 'title', 'user_code', 'department', 'user',
                    'percentage_discount', 'number_of_uses', 'start_date',
                    'end_date')
    list_display_links = ('id', 'title', 'user_code')
    list_filter = (
        'department',
        'user',
        ('start_date', DateRangeFilter),
        ('end_date', DateRangeFilter),
    )
    search_fields = ('=pk', 'user__username', 'department__username', 'code')

    readonly_fields = ('created', 'modified', 'created_by', 'modified_by',
                       'user_code')
    raw_id_fields = ('department', 'user')
    form = make_ajax_form(Discount, {
        'user': 'users',
        'department': 'departments',
    })
    fieldsets = (
        ('General', {
            'fields':
            ('title', 'description', 'percentage_discount', 'number_of_uses',
             'start_date', 'end_date', 'code', 'user_code')
        }),
        ('Options', {
            'fields': ('department', 'user', 'created', 'modified',
                       'created_by', 'modified_by')
        }),
    )
    list_select_related = ('department', 'user', 'user__profile')

    def get_queryset(self, request):
        self.user = request.user
        return super().get_queryset(request)

    def user_code(self, obj=None):
        return obj.get_code(self.user)


@admin.register(Subscription)
class SubsctriptionAdmin(AdminRowActionsMixin, VersionAdmin, JsonAdmin):
    """
    The subscription admin interface
    """
    list_display = ('id', 'subscription', 'client', 'status', 'period',
                    'price', 'created', 'modified')
    list_display_links = ('id', 'subscription')
    list_filter = (
        'status',
        'period',
        ('client__login', TextFieldListFilter),
        ('created', DateRangeFilter),
    )
    search_fields = ('=pk', '=order__pk', 'client__email', 'client__name',
                     'client__login')
    readonly_fields = ('merchant', 'customer', 'subscription', 'created',
                       'modified', 'created_by', 'modified_by')
    raw_id_fields = ('order', 'client')
    form = make_ajax_form(Subscription, {
        'client': 'clients',
    })
    fieldsets = (
        ('General', {
            'fields': ('client', 'order', 'country', 'status', 'period',
                       'price')
        }),
        ('Options', {
            'fields': ('merchant', 'customer', 'subscription', 'created',
                       'modified', 'created_by', 'modified_by')
        }),
    )
    list_select_related = ('order', 'client')

    def get_row_actions(self, obj):
        row_actions = [
            {
                'label': 'Info',
                'action': 'info'
            },
            {
                'label': 'Cancel',
                'action': 'cancel',
                'enabled': obj.status == 'enabled'
            },
        ]
        row_actions += super().get_row_actions(obj)
        return row_actions

    def info(self, request, obj):
        braintree = BraintreeGateway(obj.country, 'sandbox')
        result = braintree.get_subscription(obj.subscription)
        return HttpResponse(
            jsonpickle.encode(result), content_type='application/json')

    def cancel(self, request, obj):
        """
        Install client
        """
        obj.cancel()
        self.message_user(request, _('The subscription have canceled.'))

    class Media:
        js = ('js/admin/subscription.js', )


@admin.register(Transaction)
class TransactionAdmin(VersionAdmin, JsonAdmin):
    """
    Transaction admin interface
    """
    list_display = ('id', 'order', 'created', 'modified')
    list_display_links = ('id', )
    list_filter = (
        ('order', TextFieldListFilter),
        ('created', DateRangeFilter),
    )
    search_fields = ('=pk', '=order__pk', 'order__client__name',
                     'order__client__email', 'order__client__login')
    readonly_fields = ('created', 'modified', 'created_by', 'modified_by')
    raw_id_fields = ('order', )
    fieldsets = (
        ('General', {
            'fields': (
                'order',
                'data',
            )
        }),
        ('Options', {
            'fields': ('created', 'modified', 'created_by', 'modified_by')
        }),
    )
    list_select_related = ('order', )


class TransactionInlineAdmin(admin.TabularInline):
    """
    Transaction inline admin interface
    """
    model = Transaction
    fields = ('data', 'modified')
    readonly_fields = fields
    show_change_link = True
    can_delete = False

    def has_add_permission(self, *args, **kwargs):
        return False


@admin.register(Order)
class OrderAdmin(AdminRowActionsMixin, VersionAdmin, AjaxSelectAdmin,
                 ManagerListMixin, TabbedExternalJqueryTranslationAdmin):
    """
    Order admin interface
    """
    list_display = ('id', 'price', 'status', 'client', 'expired_date',
                    'paid_date', 'payment_system', 'created', 'modified')
    list_display_links = (
        'id',
        'price',
    )
    list_filter = (
        'status',
        'client_services__service',
        'client_services__service',
        ('client_services', TextFieldListFilter),
        ('client__login', TextFieldListFilter),
        'payment_system',
        ('expired_date', DateRangeFilter),
        ('paid_date', DateRangeFilter),
        ('created', DateRangeFilter),
    )
    search_fields = ('=pk', '=client_services__pk',
                     'client_services__service__title',
                     'client_services__service__description', 'client__name',
                     'client__email', 'client__login')
    readonly_fields = ('created', 'modified', 'created_by', 'modified_by')
    raw_id_fields = ('client', )
    inlines = (TransactionInlineAdmin, )
    fieldsets = (
        ('General', {
            'fields': ('price', 'client', 'expired_date', 'note',
                       'client_services')
        }),
        ('Options', {
            'fields': ('status', 'paid_date', 'payment_system', 'created',
                       'modified', 'created_by', 'modified_by')
        }),
    )
    form = make_ajax_form(Order, {
        'client_services': 'order_client_services',
        'client': 'clients',
    })
    list_select_related = ('client', 'client__country')

    def bill(self, obj, request=None, load=False):
        return manager.get('bill', obj, request=request, load=load)

    def bill_pdf(self, request, obj):
        bill = self.bill(obj, request, load=True)
        response = HttpResponse(bill.pdf, content_type='application/pdf')
        content = 'inline; filename=bill_{}.pdf'.format(obj.pk)
        response['Content-Disposition'] = content
        return response

    def get_row_actions(self, obj):
        row_actions = [
            {
                'label': 'Bill',
                'action': 'bill_pdf',
                'enabled': obj.status == 'new' and self.bill(obj)
            },
        ]
        row_actions += super(OrderAdmin, self).get_row_actions(obj)
        return row_actions

    class Media:
        js = ('js/admin/orders.js', )


class PriceInlineAdmin(admin.TabularInline):
    """
    Price admin interface
    """
    model = Price
    fields = ('price', 'country', 'period_from', 'period_to', 'for_unit',
              'is_enabled', 'created', 'modified', 'created_by', 'modified_by')
    raw_id_fields = ('country', )
    readonly_fields = ('created', 'modified', 'created_by', 'modified_by')
    extra = 0


class ServiceInlineAdmin(admin.TabularInline):
    """
    Service inline admin
    """
    model = Service
    fields = ('title', 'period', 'period_units', 'type', 'is_default',
              'is_enabled')

    show_change_link = True


@admin.register(ServiceCategory)
class ServiceCategoryAdmin(VersionAdmin, TabbedExternalJqueryTranslationAdmin):
    """
    ServiceCategory admin interface
    """
    list_display = ('id', 'title', 'created')
    list_display_links = ('id', 'title')
    list_filter = (('created', DateRangeFilter), )
    search_fields = ('pk', 'title', 'description', 'services__title')
    readonly_fields = ('created', 'modified', 'created_by', 'modified_by')
    inlines = (ServiceInlineAdmin, )
    fieldsets = (
        ('General', {
            'fields': (
                'title',
                'description',
            )
        }),
        ('Options', {
            'fields': ('created', 'modified', 'created_by', 'modified_by')
        }),
    )


@admin.register(Service)
class ServiceAdmin(VersionAdmin, TabbedExternalJqueryTranslationAdmin):
    """
    Service admin interface
    """
    list_display = ('id', 'title', 'category', 'period', 'period_units',
                    'type', 'is_default', 'is_enabled', 'created')
    list_select_related = ('category', )
    list_display_links = ('id', 'title')
    list_filter = ('is_enabled', 'period_units', ('created', DateRangeFilter),
                   'type', 'is_default')
    search_fields = ('pk', 'title', 'description', 'type')
    readonly_fields = ('created', 'modified', 'created_by', 'modified_by',
                       'period_days', 'price')
    inlines = (PriceInlineAdmin, )
    fieldsets = (
        ('General', {
            'fields': ('category', 'title', 'description', 'price')
        }),
        ('Options', {
            'fields':
            ('period', 'period_units', 'type', 'is_default', 'period_days',
             'is_enabled', 'created', 'modified', 'created_by', 'modified_by')
        }),
    )
