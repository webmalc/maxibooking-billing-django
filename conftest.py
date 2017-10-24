import arrow
import pytest
from django.core.management import call_command
from moneyed import EUR, Money

from finances.models import Order


@pytest.fixture(scope='session')
def django_db_setup(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        call_command('loaddata', 'tests/users', 'tests/countries',
                     'tests/regions', 'tests/cities', 'tests/clients',
                     'tests/properties', 'tests/rooms', 'tests/services',
                     'tests/client_services')


@pytest.fixture()
def make_orders():
    now = arrow.utcnow()
    order = Order()
    order.client_id = 1
    order.price = Money(12500, EUR)
    order.status = 'new'
    order.note = 'payment notification'
    order.expired_date = now.shift(days=2).datetime
    order.save()

    order.pk = None
    order.status = 'paid'
    order.note = 'paid order'
    order.save()

    order.pk = None
    order.status = 'new'
    order.note = 'order expired'
    order.expired_date = now.shift(days=-1).datetime
    order.save()

    order.pk = None
    order.status = 'new'
    order.note = None
    order.expired_date = now.shift(days=5).datetime

    return None
