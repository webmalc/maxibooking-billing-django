# -*- coding: utf-8 -*-
"""
Django firewall admin classes
"""
from django.contrib import admin
from django.core.urlresolvers import reverse
from ordered_model.admin import OrderedModelAdmin

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
class RuleAdmin(CommonAdminMixin, OrderedModelAdmin):
    """
    Rule admin interface
    """
    form = RuleForm

    def get_list_display(self, request):
        list_display = super().get_list_display(request)
        list_display[2:2] = ['url', 'get_groups']
        list_display.insert(-2, 'is_allow')
        list_display.append('move_up_down_links')
        return list_display

    def get_list_filter(self, request):
        return super().get_list_filter(request) + ['groups']

    def get_search_fields(self, request):
        return super().get_search_fields(request) + ['group__name']

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        fieldsets[0][1]['fields'][2:2] = ['url', 'groups', 'is_allow']
        return fieldsets

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('groups')

    def get_groups(self, obj):
        """
        Get rule groups as string
        """
        return ' '.join([
            '<a href="{}">{}</a>'.format(
                reverse('admin:firewall_group_change', args=[g.pk]), g)
            for g in obj.groups.all()
        ])

    get_groups.allow_tags = True
