import adminactions.actions as actions
from django.contrib import admin
from django.contrib.admin import site
from django.contrib.postgres.fields import JSONField
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django_admin_row_actions import AdminRowActionsMixin
from prettyjson import PrettyJSONWidget
from rangefilter.filter import DateRangeFilter
from reversion.admin import VersionAdmin

from .models import Comment

actions.add_to_site(site)


class TextFieldListFilter(admin.ChoicesFieldListFilter):
    template = "filters/text_field.html"

    def choices(self, changelist):
        yield {
            'selected':
            False,
            'query_string':
            changelist.get_query_string({
                self.lookup_kwarg: 0
            }, [self.lookup_kwarg_isnull]),
            'query_param':
            self.lookup_kwarg,
            'display':
            self.field
        }


class JsonAdmin(admin.ModelAdmin):
    formfield_overrides = {
        JSONField: {
            'widget': PrettyJSONWidget(attrs={'initial': 'parsed'})
        }
    }


class ShowAllInlineAdminMixin(admin.TabularInline):
    def get_formset(self, request, obj=None, **kwargs):
        self.parent_obj = obj
        return super().get_formset(request, obj, **kwargs)

    def all(self, request):
        template = """
        <a href="{}?client__login__exact={}" target="_blank">Show all</a>
        """
        return template.format(reverse(self.all_url), self.parent_obj.login)

    all.allow_tags = True


class ManagerListMixin(admin.ModelAdmin):
    """
    Change list with list_manager perm
    """

    def has_view_permission(self, request, obj=None):
        opts = self.opts
        if request.user.has_perm('{}.list_manager'.format(opts.app_label)):
            return True
        return super().has_view_permission(request, obj)

    def get_queryset(self, request):
        query = super().get_queryset(request)
        if not super().has_view_permission(request):
            query = query.filter(client__manager=request.user)
        return query


class ChangePermissionBaseMixin():
    """
    Get permission based on user permission and owner of an entry
    """

    def _get_permissions(self, request):
        opts = self.opts
        user = request.user
        own_perm = user.has_perm('{}.change_own'.format(opts.app_label))
        department_perm = user.has_perm('{}.change_department'.format(
            opts.app_label))
        return (own_perm, department_perm)

    def check_change_permission(self, result, request, obj=None):
        user = request.user
        own_perm, department_perm = self._get_permissions(request)

        if result:
            return result
        if own_perm and (not obj or obj.manager == user):
            return True
        if department_perm:
            query = self.model.objects.filter_by_department(user)
            if not obj or query.filter(pk=obj.pk).count():
                return True

        return False

    def check_delete_permission(self, result, change):
        if result:
            return result
        return change

    def fetch_queryset(self, request, query, change):
        user = request.user
        own_perm, department_perm = self._get_permissions(request)
        if not change:
            if own_perm:
                query = self.model.objects.filter_by_manager(user, query)
            if department_perm:
                query = self.model.objects.filter_by_department(user, query)
        return query


class ChangePermissionMixin(admin.ModelAdmin, ChangePermissionBaseMixin):
    def has_change_permission(self, request, obj=None):
        change = super().has_change_permission(request, obj)
        return self.check_change_permission(change, request, obj)

    def get_queryset(self, request):
        query = super().get_queryset(request)
        change = super().has_change_permission(request)
        return self.fetch_queryset(request, query, change)

    def has_delete_permission(self, request, obj=None):
        change = super().has_change_permission(request, obj)
        delete = super().has_delete_permission(request, obj)
        return self.check_delete_permission(delete, change)


class ChangePermissionInlineMixin(admin.TabularInline,
                                  ChangePermissionBaseMixin):
    def has_change_permission(self, request, obj=None):
        change = super().has_change_permission(request)
        return self.check_change_permission(change, request)

    def get_queryset(self, request):
        query = super().get_queryset(request)
        change = super().has_change_permission(request)
        return self.fetch_queryset(request, query, change)

    def has_delete_permission(self, request, obj=None):
        change = super().has_change_permission(request)
        delete = super().has_delete_permission(request)
        return self.check_delete_permission(delete, change)


class ManagerInlineListMixin(admin.TabularInline):
    """
    Change list with list_manager perm
    """

    def has_change_permission(self, request, obj=None):
        opts = self.opts
        if request.user.has_perm('{}.list_manager'.format(opts.app_label)):
            return True
        return super().has_change_permission(request, obj)

    def get_queryset(self, request):
        query = super().get_queryset(request)
        if not super().has_change_permission(request):
            query = query.filter(client__manager=request.user)
        return query


class ArchorAdminMixin(admin.ModelAdmin):
    """
    Admin with list archors
    """

    def num(self, obj):
        return '<a name="el_{0}"/>{0}'.format(obj.pk)

    num.allow_tags = True

    def response_post_save_change(self, request, obj):
        parent = super().response_post_save_change(request, obj)
        return redirect('{}#el_{}'.format(parent.url, obj.pk))

    def response_post_save_add(self, request, obj):
        return self.response_post_save_change(request, obj)


class ChangeOwnMixin():
    """
    Change created by user object only
    """

    def has_change_permission(self, request, obj=None):
        parent = super().has_change_permission(request, obj)
        if not parent:
            return parent
        if obj is not None and obj.created_by != request.user:
            return False
        return True

    def has_delete_permission(self, request, obj=None):
        parent = super().has_delete_permission(request, obj)
        if not parent:
            return parent
        if obj is not None and obj.created_by != request.user:
            return False
        return True


class DictAdminMixin():
    """
    DictAdminMixin admin interface
    """

    list_display_links = ['id', 'title']
    list_select_related = [
        'modified_by',
    ]
    search_fields = ['=pk', 'title', 'description']
    readonly_fields = [
        'code', 'created', 'modified', 'created_by', 'modified_by'
    ]
    actions = None

    def get_fieldsets(self, request, obj=None):
        return [
            ['General', {
                'fields': ['title', 'description']
            }],
            [
                'Options', {
                    'fields': [
                        'is_enabled', 'code', 'created', 'modified',
                        'created_by', 'modified_by'
                    ]
                }
            ],
        ]

    def get_list_display(self, request):
        return ['id', 'title', 'code', 'is_enabled', 'modified', 'modified_by']

    def has_delete_permission(self, request, obj=None):
        parent = super().has_delete_permission(request, obj)
        if parent and obj and obj.code:
            return False
        return parent


class CommentActionsListFilter(admin.SimpleListFilter):
    title = _('my actions')

    parameter_name = 'my_actions'

    def lookups(self, request, model_admin):
        return (('open', _('Open')), ('all', _('All')))

    def queryset(self, request, queryset):
        filtered_queryset = queryset.filter(
            type='action', created_by=request.user)
        if self.value() == 'all':
            return filtered_queryset
        elif self.value() == 'open':
            return filtered_queryset.filter(status__isnull=True)
        return queryset


@admin.register(Comment)
class CommentAdmin(ChangeOwnMixin, AdminRowActionsMixin, VersionAdmin):
    """
    Comments admin interface
    """
    list_display = ('id', 'text', 'date', 'status', 'type', 'client',
                    'created', 'created_by')
    list_display_links = ('id', )
    actions = None
    list_filter = (CommentActionsListFilter, 'type', 'status',
                   ('date', DateRangeFilter), ('created',
                                               DateRangeFilter), 'created_by')
    search_fields = ('=pk', 'text')
    readonly_fields = ('created', 'modified', 'created_by', 'modified_by')
    fieldsets = (
        ('General', {
            'fields': ('text', 'date', 'type', 'status')
        }),
        ('Options', {
            'fields': ('created', 'modified', 'created_by', 'modified_by')
        }),
    )
    list_select_related = ('created_by', )

    def set_completed(self, request, obj):
        obj.status = 'completed'
        obj.save()
        self.message_user(request, _('Action is marked as completed.'))

    def set_canceled(self, request, obj):
        obj.status = 'canceled'
        obj.save()
        self.message_user(request, _('Action is marked as canceled.'))

    def get_row_actions(self, obj):
        def enabled():
            return obj.type == 'action' and not obj.status

        row_actions = [
            {
                'label': 'complete',
                'action': 'set_completed',
                'enabled': enabled()
            },
            {
                'label': 'cancel',
                'action': 'set_canceled',
                'enabled': enabled()
            },
        ]

        row_actions += super().get_row_actions(obj)
        return row_actions

    def client(self, obj):
        client_id = obj.object_id
        template = """
        <a href="{}" target="_blank">{}</a>
        """
        return template.format(
            reverse('admin:clients_client_change', args=[client_id]),
            client_id,
        )

    client.allow_tags = True

    class Media:
        js = ('js/admin/comments.js', )
