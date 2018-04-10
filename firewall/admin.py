# -*- coding: utf-8 -*-
"""
Django firewall admin classes
"""
from django.contrib import admin
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from ordered_model.admin import OrderedModelAdmin

from .forms import IpRangeFormSet, RuleForm
from .models import Group, IpRange, Rule
from .settings import FIREWALL_IPRANGES_ADMIN_MAX


class IpRangeInlineAdmin(admin.TabularInline):
    """
    Ip admin
    """
    model = IpRange
    formset = IpRangeFormSet
    extra = 2
    readonly_fields = ['options']
    fields = [
        'start_ip', 'end_ip', 'start_date', 'end_date', 'is_enabled', 'options'
    ]
    verbose_name_plural = _('Last %(max)d ip ranges') % {
        'max': FIREWALL_IPRANGES_ADMIN_MAX
    }

    def options(self, obj):
        """
        Get rule groups as string
        """
        return '<br>'.join([
            obj.modified.strftime('%d.%m.%Y %H:%M'), obj.modified_by.username
        ])

    options.allow_tags = True


class CommonAdminMixin(admin.ModelAdmin):
    """
    Base admin
    """
    list_display_links = ['id', 'name']
    readonly_fields = ['created', 'modified', 'created_by', 'modified_by']
    inlines = [IpRangeInlineAdmin]

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


@admin.register(IpRange)
class IpRangeAdmin(admin.ModelAdmin):
    """
    Group admin interface
    """
    list_display = [
        'id', 'start_ip', 'end_ip', 'start_date', 'end_date', 'group', 'rule',
        'is_enabled', 'modified', 'modified_by'
    ]
    list_display_links = ['id', 'start_ip', 'end_ip']
    readonly_fields = ['created', 'modified', 'created_by', 'modified_by']
    list_filter = ['is_enabled', 'group', 'rule', 'modified']
    list_select_related = ['modified_by', 'rule', 'group']
    search_fields = [
        'start_ip', 'end_ip', 'group__name', 'rule__name', 'rule__description',
        'group__description'
    ]

    fieldsets = [
        [
            'General', {
                'fields': [
                    'start_ip',
                    'end_ip',
                    'start_date',
                    'end_date',
                    'group',
                    'rule',
                ]
            }
        ],
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
