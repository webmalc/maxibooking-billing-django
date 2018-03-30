# -*- coding: utf-8 -*-
"""
Django firewall admin classes
"""
from django.contrib import admin

from .forms import RuleForm
from .models import Group, Rule


class CommonAdminMixin(admin.ModelAdmin):
    """
    Base admin
    """
    list_display_links = ['id', 'name']
    readonly_fields = ['created', 'modified', 'created_by', 'modified_by']

    def get_list_display(self, request):
        return [
            'id',
            'name',
            'entries',
            'is_enabled',
            'modified',
        ]

    def get_list_filter(self, request):
        return ['is_enabled', 'modified', 'created']

    def get_search_fields(self, request):
        return [
            '=pk',
            'name',
            'description',
            'entries',
            'created_by__username',
            'created_by__email',
            'created_by__last_name',
            'modified_by__username',
            'modified_by__last_name',
        ]

    def get_fieldsets(self, request, obj=None):
        return [
            ['General', {
                'fields': [
                    'name',
                    'description',
                    'entries',
                ]
            }],
            [
                'Options', {
                    'fields': [
                        'is_enabled',
                        'created',
                        'modified',
                        'created_by',
                        'modified_by',
                    ]
                }
            ],
        ]

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        obj.modified_by = request.user
        obj.save()

    class Media:
        css = {'all': ('css/admin/firewall.css', )}


@admin.register(Group)
class GroupAdmin(CommonAdminMixin):
    """
    Group admin interface
    """
    pass


@admin.register(Rule)
class RuleAdmin(CommonAdminMixin):
    """
    Rule admin interface
    """
    form = RuleForm

    def get_list_display(self, request):
        list_display = super().get_list_display(request)
        list_display.insert(2, 'url')
        return list_display

    def get_list_filter(self, request):
        return super().get_list_filter(request) + ['groups']

    def get_search_fields(self, request):
        return super().get_search_fields(request) + [
            'group__name', 'group__entries'
        ]

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        fieldsets[0][1]['fields'][2:2] = ['url', 'groups']
        return fieldsets
