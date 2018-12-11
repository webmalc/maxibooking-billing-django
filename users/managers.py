from billing.managers import LookupMixin


class DepartmentManager(LookupMixin):
    """"
    The department manager
    """
    lookup_search_fields = ('id', 'title', 'description')
