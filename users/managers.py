from django.apps import apps

from billing.lib.utils import get_code
from billing.managers import LookupMixin


class DepartmentManager(LookupMixin):
    """"
    The department manager
    """
    lookup_search_fields = ('id', 'title', 'description')


class ProfileManager(LookupMixin):
    """"
    The department manager
    """
    lookup_search_fields = ('id', 'code')

    def get_user_by_code(self, code):
        """
        Get user by profile code
        """
        try:
            code, discount = get_code(code)
        except ValueError:
            return None
        try:
            return self.get(code=code).user
        except apps.get_model('users', 'Profile').DoesNotExist:
            return None
