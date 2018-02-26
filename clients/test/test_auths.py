import json

import pytest
from django.core.urlresolvers import reverse

from billing.lib.test import json_contains

pytestmark = pytest.mark.django_db


def test_clients_auth_list_by_user(client):
    response = client.get(reverse('clientauth-list'))
    assert response.status_code == 401


def test_clients_auth_list_by_admin(admin_client):
    response = admin_client.get(reverse('clientauth-list'))
    assert response.status_code == 200
    assert len(response.json()['results']) == 3
    json_contains(response, '127.0.0.1')


def test_client_auth_display_by_user(client):
    response = client.get(reverse('clientauth-detail', args=['1']))
    assert response.status_code == 401


def test_client_auth_display_by_admin(admin_client):
    response = admin_client.get(reverse('clientauth-detail', args=['3']))
    assert response.status_code == 200
    json_contains(response, 'user_agent 2')


def test_client_auth_create_by_admin(admin_client):
    data = json.dumps({
        'client': 'user-one',
        'auth_date': '2017-12-01T10:22:48.995041Z',
        'user_agent': 'created user agent',
        'ip': '1.1.1.1',
    })
    response = admin_client.post(
        reverse('clientauth-list'), data=data, content_type="application/json")
    response_json = response.json()

    assert response_json['client'] == 'user-one'
    assert response_json['ip'] == '1.1.1.1'

    response = admin_client.get(reverse('clientauth-list'))
    assert len(response.json()['results']) == 4
    json_contains(response, 'created user agent')
