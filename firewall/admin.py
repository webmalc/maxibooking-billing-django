# -*- coding: utf-8 -*-
"""
Django firewall admin classes
"""
from django.contrib import admin

from .models import Group, Rule


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    """
    Group admin interface
    """
    list_display = (
        'id',
        'name',
        'entries',
        'is_enabled',
        'modified',
    )
    list_display_links = ('id', 'name')
    list_filter = ('is_enabled', 'modified', 'created')
    search_fields = (
        '=pk',
        'name',
        'description',
        'entries',
        'created_by__username',
        'created_by__email',
        'created_by__last_name',
        'modified_by__username',
        'modified_by__last_name',
    )
    readonly_fields = ('created', 'modified', 'created_by', 'modified_by')
    fieldsets = (
        ('General', {
            'fields': (
                'name',
                'description',
                'entries',
            )
        }),
        ('Options', {
            'fields': (
                'is_enabled',
                'created',
                'modified',
                'created_by',
                'modified_by',
            )
        }),
    )

    class Media:
        css = {'all': ('css/admin/firewall.css', )}


@admin.register(Rule)
class RuleAdmin(admin.ModelAdmin):
    """
    Rule admin interface
    """
    list_display = (
        'id',
        'name',
        'url',
        'entries',
        'is_enabled',
        'modified',
    )
    list_display_links = ('id', 'name')
    list_filter = ('is_enabled', 'modified', 'created', 'groups')
    search_fields = (
        '=pk',
        'name',
        'description',
        'entries',
        'created_by__username',
        'created_by__email',
        'created_by__last_name',
        'modified_by__username',
        'modified_by__last_name',
        'group__name',
        'group__entries',
    )
    readonly_fields = ('created', 'modified', 'created_by', 'modified_by')
    fieldsets = (
        ('General', {
            'fields': (
                'name',
                'description',
                'url',
                'groups',
                'entries',
            )
        }),
        ('Options', {
            'fields': (
                'is_enabled',
                'created',
                'modified',
                'created_by',
                'modified_by',
            )
        }),
    )

    class Media:
        css = {'all': ('css/admin/firewall.css', )}
