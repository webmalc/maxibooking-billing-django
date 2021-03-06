import pytest
from django.core.validators import ValidationError

from finances.models import Discount
from users.models import BillingUser

pytestmark = pytest.mark.django_db


def test_discount_code_validation(discounts):
    discount = discounts[0]
    discount.code = 'adfa~'
    with pytest.raises(ValidationError) as e:
        discount.full_clean()
    assert '~ symbol is not allowed' in str(e)


def test_discount_set_user(discounts):
    discount_user = discounts[0]
    discount_department = discounts[1]

    discount = Discount()
    discount.created_by_id = 2
    discount.percentage_discount = 10
    discount.save()

    assert discount_user.manager_id == 1
    assert discount_department.manager is None
    assert discount.manager_id == 2


def test_discount_generate_code(discounts):
    discount_user = discounts[0]
    discount_department = discounts[1]

    assert discount_user.code is not None
    assert discount_user.code[0:2] == '01'
    assert discount_department.code is not None
    assert discount_department.code[0:2] == '10'


def test_discount_get_code(discounts):
    discount_user = discounts[0]
    discount_department = discounts[1]
    user_one = BillingUser.objects.get(pk=1)
    user_two = BillingUser.objects.get(pk=2)

    assert '{}~{}'.format(user_one.profile.code,
                          discount_user.code) == discount_user.get_code()
    assert '{}~{}'.format(
        user_one.profile.code,
        discount_user.code) == discount_user.get_code(user_two)

    with pytest.raises(ValueError) as e:
        discount_department.get_code()
    assert 'valid user is not defined' in str(e.value)

    assert '{}~{}'.format(
        user_one.profile.code,
        discount_department.code) == discount_department.get_code(user_one)

    assert '{}~{}'.format(
        user_two.profile.code,
        discount_department.code) == discount_department.get_code(user_two)
