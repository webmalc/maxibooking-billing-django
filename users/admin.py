from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from reversion.admin import VersionAdmin

from .models import Profile


class ProfileInline(admin.StackedInline):
    """
    Profile admin interface
    """
    fields = ('code', 'created', 'modified', 'created_by', 'modified_by')
    readonly_fields = ('created', 'modified', 'created_by', 'modified_by')
    model = Profile
    fk_name = 'user'
    can_delete = False


class UserAdmin(BaseUserAdmin, VersionAdmin):
    """
    Users admin interface
    """
    inlines = (ProfileInline, )


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
