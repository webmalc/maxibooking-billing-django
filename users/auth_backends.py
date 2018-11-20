from django.contrib.auth.backends import ModelBackend

from .models import BillingUser, Profile


class ProxiedModelBackend(ModelBackend):
    def get_user(self, user_id):
        try:
            return BillingUser.objects.get(pk=user_id)
        except BillingUser.DoesNotExist:
            return None

    def _get_group_permissions(self, user_obj):
        perms = super()._get_group_permissions(user_obj)
        try:
            department = user_obj.profile.department
            if department and department.default_group:
                perms = perms.union(department.default_group.permissions.all())
            for department in user_obj.admin_departments.all():
                if department.admin_group:
                    perms = perms.union(
                        department.admin_group.permissions.all())
        except Profile.DoesNotExist:
            pass
        return perms
