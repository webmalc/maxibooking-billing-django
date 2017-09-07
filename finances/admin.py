from django.contrib import admin
from modeltranslation.admin import TabbedExternalJqueryTranslationAdmin
from reversion.admin import VersionAdmin

from clients.models import ClientService

from .models import Order, Price, Service


class ClientServiceInlineAdmin(admin.TabularInline):
    """
    ClientServiceInline admin interface
    """
    model = ClientService.orders.through
    raw_id_fields = ('clientservice', )
    show_change_link = True
    extra = 1
    verbose_name = 'Service'
    verbose_name_plural = 'Services'


@admin.register(Order)
class OrderAdmin(VersionAdmin):
    """
    Order admin interface
    """
    list_display = ('id', 'price', 'status', 'client', 'expired_date',
                    'paid_date', 'created', 'modified')
    list_display_links = ('id', 'price', )
    list_filter = ('status', 'expired_date', 'paid_date', 'created')
    search_fields = ('id', 'client_services__pk',
                     'client_services__service__title',
                     'client_services__service__description', 'client__name',
                     'client__email', 'client__login')
    readonly_fields = ('created', 'modified', 'paid_date', 'created_by',
                       'modified_by')
    raw_id_fields = ('client', )
    inlines = (ClientServiceInlineAdmin, )
    fieldsets = (('General', {
        'fields': ('price', 'client', 'expired_date', 'note')
    }), ('Options', {
        'fields': ('status', 'paid_date', 'created', 'modified', 'created_by',
                   'modified_by')
    }), )
    list_select_related = ('client', )


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
    search_fields = ('title', 'description', 'price', 'id')
    readonly_fields = ('created', 'modified', 'created_by', 'modified_by',
                       'period_days', 'price')
    inlines = (PriceInlineAdmin, )
    fieldsets = (('General', {
        'fields': ('title', 'description', 'price')
    }), ('Options', {
        'fields':
        ('period', 'period_units', 'type', 'is_default', 'period_days',
         'is_enabled', 'created', 'modified', 'created_by', 'modified_by')
    }), )
