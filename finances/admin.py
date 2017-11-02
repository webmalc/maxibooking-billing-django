from ajax_select import make_ajax_form
from ajax_select.admin import AjaxSelectAdmin
from django.contrib import admin
from modeltranslation.admin import TabbedExternalJqueryTranslationAdmin
from reversion.admin import VersionAdmin

from billing.admin import TextFieldListFilter

from .models import Order, Price, Service


@admin.register(Order)
class OrderAdmin(VersionAdmin, AjaxSelectAdmin):
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


@admin.register(Service)
class ServiceAdmin(VersionAdmin, TabbedExternalJqueryTranslationAdmin):
    """
    Service admin interface
    """
    list_display = ('id', 'title', 'period', 'period_units', 'type',
                    'is_default', 'is_enabled', 'created')
    list_display_links = ('id', 'title')
    list_filter = ('is_enabled', 'period_units', 'created', 'type',
                   'is_default')
    search_fields = ('pk', 'title', 'description', 'type')
    readonly_fields = ('created', 'modified', 'created_by', 'modified_by',
                       'period_days', 'price')
    inlines = (PriceInlineAdmin, )
    fieldsets = (
        ('General', {
            'fields': ('title', 'description', 'price')
        }),
        ('Options', {
            'fields':
            ('period', 'period_units', 'type', 'is_default', 'period_days',
             'is_enabled', 'created', 'modified', 'created_by', 'modified_by')
        }),
    )
