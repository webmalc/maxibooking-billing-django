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
    call_command('fms', 'fms', path + 'fms.csv', 'silently')


def test_fms_list_by_user(client, import_fms):
    response = client.get(reverse('fms-list'))
    assert response.status_code == 401


def test_fms_list_by_admin(admin_client, import_fms):
    response = admin_client.get(reverse('fms-list'))
    assert response.status_code == 200
    assert len(response.json()['results']) == 5
    json_contains(response, 'МВД КАРАЧАЕВО-ЧЕРКЕССКОЙ РЕСПУБЛИКИ')


def test_fms_search_by_admin(admin_client, import_fms):
    url = reverse('fms-list') + '?' + urlencode({'search': 'ЗЕЛЕН'})
    response = admin_client.get(url)
    assert response.status_code == 200
    assert len(response.json()['results']) == 1
    json_contains(response,
                  'ЗЕЛЕНЧУКСКИЙ РОВД КАРАЧАЕВО-ЧЕРКЕССКОЙ РЕСПУБЛИКИ')


def test_fms_display_by_admin(admin_client, import_fms):
    response = admin_client.get(reverse('fms-detail', args=[3268]))
    assert response.status_code == 200
    json_contains(response, 'МАЙКОПСКИЙ РОВД РЕСПУБЛИКИ АДЫГЕЯ')


def test_fms_display_by_user(client, import_fms):
    response = client.get(reverse('fms-detail', args=[3268]))
    assert response.status_code == 401
