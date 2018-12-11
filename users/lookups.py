from ajax_select import register

from billing.lookup import BaseLookup

from .models import Department


@register('departments')
class DepartmentLookup(BaseLookup):
    model = Department
