from ajax_select import make_ajax_form
from ajax_select.admin import AjaxSelectAdmin
from django.contrib import admin
from modeltranslation.admin import TabbedExternalJqueryTranslationAdmin
from reversion.admin import VersionAdmin

from billing.admin import JsonAdmin, TextFieldListFilter

from .models import Order, Price, Service, ServiceCategory, Transaction


@admin.register(Transaction)
class TransactionAdmin(VersionAdmin, JsonAdmin):
    """
    Transaction admin interface
    """
    list_display = ('id', 'order', 'created', 'modified')
    list_display_links = ('id', )
    list_filter = (
        ('order', TextFieldListFilter),
        'created',
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
class OrderAdmin(VersionAdmin, AjaxSelectAdmin,
                 TabbedExternalJqueryTranslationAdmin):
    """
    Order admin interface
    """
    list_display = ('id', 'price', 'status', 'client', 'expired_date',
                    'paid_date', 'created', 'modified')
    list_display_links = (
        'id',
        'price',
    )
    list_filter = (
        'status',
        'client_services__service',
        ('client_services', TextFieldListFilter),
        'expired_date',
        'paid_date',
        'created',
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
    list_select_related = ('client', )

    class Media:
        js = ('js/admin/orders.js', )


class PriceInlineAdmin(admin.TabularInline):
    """
    Price admin interface
    """
    model = Price
    fields = ('price', 'country', 'is_enabled', 'created', 'modified',
              'created_by', 'modified_by')
    raw_id_fields = ('country', )
    readonly_fields = ('created', 'modified', 'created_by', 'modified_by')


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
    list_filter = ('created', )
    search_fields = ('pk', 'title', 'description', 'services_title')
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
    list_filter = ('is_enabled', 'period_units', 'created', 'type',
                   'is_default')
    search_fields = ('pk', 'title', 'description', 'type')
    readonly_fields = ('created', 'modified', 'created_by', 'modified_by',
                       'period_days', 'price')
    inlines = (PriceInlineAdmin, )
    fieldsets = (
        ('General', {
            'fields': ('category', 'title', 'description', 'price')
        }),
        ('Options', {
            'fields': ('period', 'period_units', 'type', 'is_default',
                       'period_days', 'default_rooms', 'is_enabled', 'created',
                       'modified', 'created_by', 'modified_by')
        }),
    )
