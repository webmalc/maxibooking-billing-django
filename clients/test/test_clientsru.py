import json
import arrow

from django.core.urlresolvers import reverse

from billing.lib.test import json_contains


def test_clientsru_list_by_user(client):
    response = client.get(reverse('clientru-list'))
    assert response.status_code == 401


def test_clientsru_list_by_admin(admin_client):
    response = admin_client.get(reverse('clientru-list'))
    assert response.status_code == 200
    assert len(response.json()['results']) == 2
    json_contains(response, 'issued by yoda')


def test_clientsru_display_by_admin(admin_client):
    response = admin_client.get(reverse('clientru-detail', args=['user-rus']))
    assert response.status_code == 200
    response_json = response.json()
    response_json['inn'] = '1212222222222'
    response_json['passport_issued_by'] = 'test issued by'


def test_clientsru_display_by_user(client):
    response = client.get(reverse('clientru-detail', args=['user-rus']))
    assert response.status_code == 401


def test_clientsru_create_by_admin(admin_client):
    data = {
        'client': 'invalid-user',
        'passport_serial': '12',
        'passport_number': '12',
        'passport_date': arrow.utcnow().shift(years=2).isoformat(),
        'passport_issued_by': '1',
        'inn': '1212',
    }
    url = reverse('clientru-list')
    response = admin_client.post(
        url, data=json.dumps(data), content_type="application/json")
    response_json = response.json()

    assert response_json['passport_serial'] == [
        'Ensure this field has at least 4 characters.'
    ]
    assert response_json['passport_number'] == [
        'Ensure this field has at least 6 characters.'
    ]
    assert response_json['passport_issued_by'] == [
        'Ensure this field has at least 4 characters.'
    ]
    assert response_json['inn'] == [
        'Ensure this field has at least 10 characters.'
    ]

    assert response_json['client'] == [
        'Object with login=invalid-user does not exist.'
    ]

    data = {
        'client': 'user-four',
        'passport_serial': '1234',
        'passport_number': '123456',
        'passport_date': arrow.utcnow().shift(years=2).isoformat(),
        'passport_issued_by': 'by luke',
        'inn': '1234567890',
    }

    response = admin_client.post(
        url, data=json.dumps(data), content_type="application/json")
    response_json = response.json()
    response_json = response.json()
    assert response.status_code == 201
    assert response_json['client'] == 'user-four'
    assert response_json['passport_serial'] == '1234'
    assert response_json['passport_issued_by'] == 'by luke'


def test_clientsru_update_world_by_admin(admin_client):
    data = {'passport_issued_by': 'by obi-wan'}
    url = reverse('clientru-detail', args=['user-rus'])
    response = admin_client.patch(
        url, data=json.dumps(data), content_type="application/json")
    response_json = response.json()

    assert response.status_code == 200
    assert response_json['passport_issued_by'] == 'by obi-wan'
