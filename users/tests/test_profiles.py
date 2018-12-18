import pytest
from django.contrib.auth.models import Group, User
from django.core.validators import ValidationError

from clients.models import Client
from users.models import BillingUser, Department

pytestmark = pytest.mark.django_db


def test_profile_code_generate():
    user = User.objects.create_user(
        username='Bob',
        email='bob@example.com',
        password='password',
    )
    assert user.profile is not None
    assert user.profile.code[0] == str(user.id)


def test_profile_code_validation():
    admin = BillingUser.objects.get(username='admin')
    admin.profile.code = 'adfa~'
    with pytest.raises(ValidationError) as e:
        admin.profile.full_clean()
    assert '~ symbol is not allowed' in str(e)


def test_query_filter_by_department():
    admin = BillingUser.objects.get(username='admin')
    test = BillingUser.objects.get(username='test')
    clients = Client.objects.filter_by_department(admin)

    assert clients.count() == 1
    assert clients[0].manager == test

    Client.objects.filter(pk=1).update(manager=test)
    clients = Client.objects.filter_by_department(admin).order_by('pk')

    assert clients.count() == 2


def test_department_group_permissions(permissions):
    group_one = Group.objects.get(name='test_group_one')
    group_three = Group.objects.get(name='test_group_three')
    department = Department.objects.get(title='managers')

    manager_user = User.objects.get(username='manager')
    assert manager_user.has_perm('clients.test_client_permission_one') is False

    group_one.user_set.add(manager_user)
    manager_user = User.objects.get(username='manager')

    assert manager_user.has_perm('clients.test_client_permission_one')
    assert manager_user.has_perm('clients.test_client_permission_two') is False
    assert manager_user.has_perm(
        'clients.test_client_permission_three') is False

    profile = manager_user.profile
    profile.department = department
    profile.save()

    manager_user = User.objects.get(username='manager')
    manager_user.profile.refresh_from_db()

    manager_user.get_group_permissions()
    assert manager_user.has_perm('clients.test_client_permission_one')
    assert manager_user.has_perm('clients.test_client_permission_two')
    assert manager_user.has_perm(
        'clients.test_client_permission_three') is False

    department = manager_user.profile.department
    department.admin = manager_user
    department.save()
    manager_user = User.objects.get(username='manager')

    assert manager_user.has_perm('clients.test_client_permission_one')
    assert manager_user.has_perm('clients.test_client_permission_two')
    assert manager_user.has_perm('clients.test_client_permission_three')

    department = manager_user.profile.department
    department.default_group = None
    department.admin = None
    department.save()
    manager_user = User.objects.get(username='manager')

    assert manager_user.profile.department.default_group is None
    assert manager_user.has_perm('clients.test_client_permission_one')
    assert manager_user.has_perm('clients.test_client_permission_two') is False
    assert manager_user.has_perm(
        'clients.test_client_permission_three') is False

    department = manager_user.profile.department
    department.default_group = group_three
    department.save()
    manager_user = User.objects.get(username='manager')

    assert manager_user.profile.department.default_group == group_three
    assert manager_user.has_perm('clients.test_client_permission_one')
    assert manager_user.has_perm('clients.test_client_permission_two') is False
    assert manager_user.has_perm('clients.test_client_permission_three')
