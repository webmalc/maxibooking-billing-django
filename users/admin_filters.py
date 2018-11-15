from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from .models import Department


class UserDepartmentListFilter(admin.SimpleListFilter):
    """
    Filter users by a profile department
    """
    title = _('department')

    parameter_name = 'department'

    def lookups(self, request, model_admin):
        return [(d.id, d.title) for d in Department.objects.all()]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(profile__department__id=self.value())
