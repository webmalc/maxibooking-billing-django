from urllib.parse import urlencode

import pytest
from django.conf import settings
from django.core.management import call_command
from django.urls import reverse

from billing.lib.test import json_contains

pytestmark = pytest.mark.django_db


@pytest.fixture()
def import_fms():
    path = settings.FIXTURE_DIRS[0] + '/tests/'
    call_command('fms', 'kpp', path + 'kpp.csv', 'silently')


def test_kpp_list_by_user(client, import_fms):
    response = client.get(reverse('kpp-list'))
    assert response.status_code == 401


def test_kpp_list_by_admin(admin_client, import_fms):
    response = admin_client.get(reverse('kpp-list'))
    assert response.status_code == 200
    assert len(response.json()['results']) == 7
    json_contains(response, 'ПОЯРКОВО')


def test_kpp_search_by_admin(admin_client, import_fms):
    url = reverse('kpp-list') + '?' + urlencode({'search': 'КОНС'})
    response = admin_client.get(url)
    assert response.status_code == 200
    assert len(response.json()['results']) == 1
    json_contains(response, 'КОНСТАНТИНОВКА (АВТО)')


def test_kpp_display_by_admin(admin_client, import_fms):
    response = admin_client.get(reverse('kpp-detail', args=[112878]))
    assert response.status_code == 200
    json_contains(response, 'ПРОВИДЕНИЯ')


def test_kpp_display_by_user(client, import_fms):
    response = client.get(reverse('kpp-detail', args=[112878]))
    assert response.status_code == 401
