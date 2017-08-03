import json

import arrow
from django.core.urlresolvers import reverse

from billing.lib.test import json_contains


def test_client_services_list_by_user(client):
    response = client.get(reverse('clientservice-list'))
    assert response.status_code == 401


def test_client_services_list_by_admin(admin_client):
    response = admin_client.get(reverse('clientservice-list'))
    assert response.status_code == 200
    assert len(response.json()['results']) == 4
    json_contains(response, '12001.85')


def test_client_service_display_by_admin(admin_client):
    response = admin_client.get(reverse('clientservice-detail', args=[1]))
    assert response.status_code == 200
    json_contains(response, '1999.98')
    json_contains(response, 'user-one')


def test_client_service_display_by_user(client):
    response = client.get(reverse('clientservice-detail', args=[1]))
    assert response.status_code == 401


def test_client_service_create_invalid_by_admin(admin_client):
    data = {
        'quantity': -3,
        'client': 'invalid-user',
        'service': 312,
        'begin': arrow.utcnow().isoformat(),
        'end': arrow.utcnow().shift(days=-3).isoformat()
    }
    response = admin_client.post(
        reverse('clientservice-list'),
        data=json.dumps(data),
        content_type="application/json")
    response_json = response.json()

    assert response_json[
        'quantity'] == ['Ensure this value is greater than or equal to 1.']
    assert response_json[
        'service'] == ['Invalid pk "312" - object does not exist.']
    assert response_json[
        'client'] == ['Object with login=invalid-user does not exist.']

    data['quantity'] = 1
    data['client'] = 'user-one'
    data['service'] = 1
    response = admin_client.post(
        reverse('clientservice-list'),
        data=json.dumps(data),
        content_type="application/json")
    response_json = response.json()

    assert response_json['non_field_errors'] == [
        'The fields client, is_enabled, service must make a unique set.'
    ]

    data['service'] = 3
    response = admin_client.post(
        reverse('clientservice-list'),
        data=json.dumps(data),
        content_type="application/json")
    response_json = response.json()

    assert response_json['non_field_errors'] == ['Please correct dates.']

    data['end'] = arrow.utcnow().shift(months=+3).isoformat()
    response = admin_client.post(
        reverse('clientservice-list'),
        data=json.dumps(data),
        content_type="application/json")
    response_json = response.json()


def test_client_service_create_by_admin(admin_client):
    data = {
        'quantity': 2,
        'client': 'user-one',
        'service': 2,
        'begin': arrow.utcnow().isoformat(),
        'end': arrow.utcnow().shift(months=+3).isoformat()
    }
    response = admin_client.post(
        reverse('clientservice-list'),
        data=json.dumps(data),
        content_type="application/json")
    response_json = response.json()
    assert response_json['price'] == '7000.00'
    assert response_json['client'] == 'user-one'
    assert response_json['is_enabled'] is True
    assert response_json['country'] == 'ad'
