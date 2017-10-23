import pytest
from django.core.management import call_command


@pytest.fixture(scope='session')
def django_db_setup(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        call_command('loaddata', 'tests/users', 'tests/countries',
                     'tests/regions', 'tests/cities', 'tests/clients',
                     'tests/properties', 'tests/rooms', 'tests/services',
                     'tests/client_services')
