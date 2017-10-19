from django.contrib import admin
from reversion.admin import VersionAdmin

from .models import Fms, Kpp


class BaseAdmin(VersionAdmin):
    list_display = ('id', 'internal_id', 'name', 'code', 'end_date')
    list_display_links = ('id', 'internal_id')
    search_fields = ('id', 'internal_id', 'name', 'code', 'end_date')
    readonly_fields = ('created', 'modified', 'created_by', 'modified_by')
    fieldsets = (('General', {
        'fields': ('internal_id', 'name', 'code', 'end_date')
    }), ('Options', {
        'fields': ('created', 'modified', 'created_by', 'modified_by')
    }), )


@admin.register(Fms)
class FmsAdmin(BaseAdmin):
    """
    Fms admin interface
    """


@admin.register(Kpp)
class KppAdmin(BaseAdmin):
    """
    Kpp admin interface
    """
