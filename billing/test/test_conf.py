import pytest
from billing.lib.conf import get_settings
from clients.models import Client
from hotels.models import Country

pytestmark = pytest.mark.django_db


def test_get_settings(settings):
    settings.TEST_PARAM = 'global'
    client = Client.objects.get(pk=1)
    assert get_settings('TEST_PARAM') == 'global'
    settings.MB_SETTINGS_BY_COUNTRY['TEST_PARAM'] = {
        '__all__': 'all',
        'ae': 'ae_val'
    }
    assert get_settings('TEST_PARAM') == 'all'
    assert get_settings('TEST_PARAM', 'us') == 'all'
    assert get_settings('TEST_PARAM', 'ae') == 'ae_val'
    assert get_settings('TEST_PARAM', Country.objects.get(pk=2)) == 'ae_val'
    assert get_settings('TEST_PARAM', client=client) == 'all'
    settings.MB_SETTINGS_BY_COUNTRY['TEST_PARAM']['us'] = {'test': 11}
    assert get_settings('TEST_PARAM', client=client) == {'test': 11}
    settings.MB_COUNTRIES_OVERWRITE = {'ff': 'ae'}
    assert get_settings('TEST_PARAM', 'ff') == 'ae_val'
