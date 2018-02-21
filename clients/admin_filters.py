from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from .models import Client


class ClientIsPaidListFilter(admin.SimpleListFilter):
    """
    Filter clients by paid orders
    """
    title = _('paid status')

    parameter_name = 'paid'

    def lookups(self, request, model_admin):
        return (('1', _('Paid')), ('0', _('Not paid')))

    def queryset(self, request, queryset):
        manager = Client.objects
        if self.value():
            return manager.get_by_orders((self.value() == '1'), queryset)
