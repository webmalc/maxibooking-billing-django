from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import Permission
from django.db.models import Q

from .models import BillingUser, Profile


class ProxiedModelBackend(ModelBackend):
    def get_user(self, user_id):
        try:
            return BillingUser.objects.get(pk=user_id)
        except BillingUser.DoesNotExist:
            return None

    def _get_group_permissions(self, user_obj):

        user_groups_field = get_user_model()._meta.get_field('groups')
        user_groups_query = 'group__%s' % user_groups_field.related_query_name(
        )
        query = Permission.objects.all()
        filters = Q(**{user_groups_query: user_obj})
        try:
            department = user_obj.profile.department
            if department and department.default_group:
                filters = filters | Q(group=department.default_group)
            for department in user_obj.admin_departments.all():
                if department.admin_group:
                    filters = filters | Q(group=department.admin_group)
        except Profile.DoesNotExist:
            pass
        return query.filter(filters)
