import arrow
import pytest
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management import call_command
from django.core.validators import ValidationError
from moneyed import EUR, RUB, Money

from clients.models import Client
from finances.models import Discount, Order, Price, Service
from hotels.models import Country
from users.models import Department


@pytest.fixture(scope='session')
def django_db_setup(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        call_command('loaddata', 'tests/users', 'tests/countries',
                     'tests/regions', 'tests/cities', 'tests/clients',
                     'tests/properties', 'tests/rooms',
                     'tests/service_categories', 'tests/services',
                     'tests/auth', 'tests/client_services',
                     'tests/transactions', 'tests/companies',
                     'tests/sales_statuses', 'tests/refusal_reasons',
                     'tests/exchange_rates')


@pytest.fixture()
def discounts():
    discount = Discount()
    discount.title = 'user_discount'
    discount.manager_id = 1
    discount.start_date = arrow.utcnow().shift(days=-1).datetime
    discount.percentage_discount = 10
    discount.save()

    discount_department = Discount()
    discount.title = 'department_discount'
    discount_department.department_id = 1
    discount_department.percentage_discount = 10
    discount_department.save()

    return discount, discount_department


@pytest.fixture()
def permissions():
    content_type = ContentType.objects.get_for_model(Client)
    permission_one = Permission.objects.create(
        codename='test_client_permission_one',
        name='test client permission one',
        content_type=content_type,
    )
    permission_two = Permission.objects.create(
        codename='test_client_permission_two',
        name='test client permission two',
        content_type=content_type,
    )
    permission_three = Permission.objects.create(
        codename='test_client_permission_three',
        name='test client permission three',
        content_type=content_type,
    )
    group_one = Group()
    group_one.name = 'test_group_one'
    group_one.save()
    group_one.permissions.add(permission_one)

    group_two = Group()
    group_two.name = 'test_group_two'
    group_two.save()
    group_two.permissions.add(permission_two)

    group_three = Group()
    group_three.name = 'test_group_three'
    group_three.save()
    group_three.permissions.add(permission_three)

    department = Department()
    department.title = 'managers'
    department.default_group = group_two
    department.admin_group = group_three
    department.save()


@pytest.fixture()
def make_comments():
    client1 = Client.objects.get(pk=1)
    client2 = Client.objects.get(pk=2)

    client1.comments.create(text='test message comment 1')
    client2.comments.create(text='test message comment 2')
    client1.comments.create(text='test action comment 1', type='action')
    client1.comments.create(text='test refusal comment 1', type='refusal')
    client1.comments.create(
        text='test action completed comment 1',
        type='action',
        status='completed',
    )
    client2.comments.create(
        text='test action canceled comment 1',
        type='action',
        status='canceled',
    )
    client1.comments.create(text='test action uncompleted comment 1',
                            type='action',
                            date=arrow.utcnow().shift(days=-1).datetime)
    client2.comments.create(text='test action uncompleted comment 2',
                            type='action',
                            date=arrow.utcnow().shift(hours=-5).datetime)
    client2.comments.create(text='test action old uncompleted comment 2',
                            type='action',
                            date=arrow.utcnow().shift(days=-15).datetime)


@pytest.fixture()
def make_prices():
    service = Service.objects.get(pk=4)
    country = Country.objects.get(pk=1)
    service.prices.all().delete()

    # SUCCESS: add base price
    price = Price()
    price.service = service
    price.price = Money(120, EUR)
    price.full_clean()
    price.save()

    # ERROR: add another base price
    with pytest.raises(ValidationError) as e:
        price.pk = None
        price.full_clean()
        price.save()
    assert 'Base price for this country already exists' in e.value.messages

    # SUCCESS: add base country price
    price.pk = None
    price.country = country
    price.price = Money(75, EUR)
    price.full_clean()
    price.save()

    # ERROR: add another base price
    with pytest.raises(ValidationError) as e:
        price.pk = None
        price.full_clean()
        price.save()
    assert 'Base price for this country already exists' in e.value.messages
    assert service.prices.all().count() == 2

    # SUCCESS: add base period price 5-10
    price.pk = None
    price.country = None
    price.price = Money(40, EUR)
    price.period_from = 5
    price.period_to = 10
    price.full_clean()
    price.save()

    # ERROR: add another period price 5-10
    with pytest.raises(ValidationError) as e:
        price.pk = None
        price.full_clean()
        price.save()
    assert 'Price with this period already exists' in e.value.messages

    # SUCCESS: add country period price 5-10
    price.pk = None
    price.country = country
    price.price = Money(122, EUR)
    price.for_unit = False
    price.full_clean()
    price.save()

    # ERROR: add another period price 6-7
    with pytest.raises(ValidationError) as e:
        price.pk = None
        price.country = None
        price.period_from = 6
        price.period_to = 7
        price.full_clean()
        price.save()
    assert 'Price with this period already exists' in e.value.messages

    # ERROR: add another period price 7-14
    with pytest.raises(ValidationError) as e:
        price.pk = None
        price.country = None
        price.period_from = 7
        price.period_to = 14
        price.full_clean()
        price.save()
    assert 'Price with this period already exists' in e.value.messages

    # ERROR: add another period price 2-7
    with pytest.raises(ValidationError) as e:
        price.pk = None
        price.country = None
        price.period_from = 2
        price.period_to = 7
        price.full_clean()
        price.save()
    assert 'Price with this period already exists' in e.value.messages

    # ERROR: add another period price 10-12
    with pytest.raises(ValidationError) as e:
        price.pk = None
        price.country = None
        price.period_from = 10
        price.period_to = 12
        price.full_clean()
        price.save()
    assert 'Price with this period already exists' in e.value.messages

    # SUCCESS: add base period price 11-∞
    price.pk = None
    price.price = Money(15, EUR)
    price.period_from = 11
    price.for_unit = True
    price.period_to = None
    price.full_clean()
    price.save()

    # SUCCESS: add base period price ∞-4
    price.pk = None
    price.price = Money(15, EUR)
    price.period_from = None
    price.period_to = 4
    price.full_clean()
    price.save()

    # ERROR: add another period price 22-33
    with pytest.raises(ValidationError) as e:
        price.pk = None
        price.country = None
        price.period_from = 22
        price.period_to = 33
        price.full_clean()
        price.save()
    assert 'Price with this period already exists' in e.value.messages

    # ERROR: add another period price 1-3
    with pytest.raises(ValidationError) as e:
        price.pk = None
        price.country = None
        price.period_from = 1
        price.period_to = 3
        price.full_clean()
        price.save()
    assert 'Price with this period already exists' in e.value.messages

    # ERROR: add another country period price 5-11
    with pytest.raises(ValidationError) as e:
        price.pk = None
        price.country = country
        price.period_from = 5
        price.period_to = 11
        price.full_clean()
        price.save()
    assert 'Price with this period already exists' in e.value.messages

    # SUCCESS: add another country period price 11-20
    price.pk = None
    price.country = country
    price.price = Money(35, EUR)
    price.period_from = 11
    price.period_to = 20
    price.full_clean()
    price.save()

    price.pk = None
    price.country = Country.objects.get(pk=2)
    price.price = Money(2300, RUB)
    price.full_clean()
    price.save()

    assert service.prices.all().count() == 8


@pytest.fixture()
def make_orders():
    now = arrow.utcnow()
    order = Order()
    order.pk = 1
    order.client_id = 1
    order.price = Money(12500, EUR)
    order.status = 'new'
    order.note = 'payment notification'
    order.expired_date = now.shift(days=2).datetime
    order.save()

    order.pk = 2
    order.status = 'paid'
    order.note = 'paid order'
    order.save()

    order.pk = 3
    order.status = 'new'
    order.note = 'order expired'
    order.expired_date = now.shift(days=-1).datetime
    order.save()

    order.pk = 4
    order.status = 'new'
    order.note = None
    order.expired_date = now.shift(days=5).datetime
    order.save()

    order.pk = 5
    order.status = 'new'
    order.client_id = 7
    order.price = Money(2500.50, RUB)
    order.save()

    return None
