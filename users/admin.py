from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.safestring import mark_safe
from reversion.admin import VersionAdmin

from .admin_filters import UserDepartmentListFilter
from .models import Department, Profile


class ProfileInline(admin.StackedInline):
    """
    Profile admin interface
    """
    fields = ('code', 'department', 'created', 'modified', 'created_by',
              'modified_by')
    readonly_fields = ('created', 'modified', 'created_by', 'modified_by')
    model = Profile
    fk_name = 'user'
    can_delete = False


class UserAdmin(BaseUserAdmin, VersionAdmin):
    """
    Users admin interface
    """
    inlines = (ProfileInline, )
    list_select_related = ('profile', 'profile__department')

    def get_list_filter(self, request):
        return list(
            super().get_list_filter(request)) + [UserDepartmentListFilter]

    def get_list_display(self, request):
        return list(super().get_list_display(request)) + ['department']

    def department(self, obj, request=None, load=False):
        try:
            profile = obj.profile
            return profile.department
        except Profile.DoesNotExist:
            return ''


admin.site.unregister(User)
admin.site.register(User, UserAdmin)


@admin.register(Department)
class DepartmentAdmin(VersionAdmin):
    """
    Department admin interface
    """
    list_display = ('id', 'title', 'country', 'admin', 'created')
    list_display_links = ('id', 'title')
    list_filter = (
        'country',
        'created',
    )
    search_fields = ('id', 'title', 'country__name',
                     'country__alternate_names', 'description',
                     'admin__username', 'admin__email', 'admin__last_name')
    raw_id_fields = ('admin', )
    readonly_fields = ('created', 'modified', 'created_by', 'modified_by',
                       'users')
    fieldsets = (
        ('General', {
            'fields': ('title', 'description', 'country')
        }),
        ('Security and permissions', {
            'fields': ('admin', 'users', 'default_group', 'admin_group',
                       'max_percentage_discount', 'min_percentage_discount')
        }),
        ('Options', {
            'fields': ('created', 'modified', 'created_by', 'modified_by')
        }),
    )
    list_select_related = ('country', 'admin')

    def users(self, obj, request=None, load=False):
        template = """
        <a href="{}?department={}" target="_blank">{}</a>
        """
        return template.format(
            reverse('admin:auth_user_changelist'),
            obj.id,
            obj.profiles.count(),
        )

    def all(self, request):
        template = """
        <a href="{}?client__login__exact={}" target="_blank">Show all</a>
        """
        return mark_safe(
            template.format(reverse(self.all_url), self.parent_obj.login))
