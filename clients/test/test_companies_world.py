import json

from django.core.urlresolvers import reverse

from billing.lib.test import json_contains


def test_companyworld_list_by_user(client):
    response = client.get(reverse('companyworld-list'))
    assert response.status_code == 401


def test_companyworld_list_by_admin(admin_client):
    response = admin_client.get(reverse('companyworld-list'))
    assert response.status_code == 200
    assert len(response.json()['results']) == 2
    json_contains(response, '1111111111_swift')


def test_companyworld_display_by_admin(admin_client):
    response = admin_client.get(reverse('companyworld-detail', args=[3]))
    assert response.status_code == 200
    response_json = response.json()
    response_json['swift'] = '1221212331_swift'
    response_json['company'] = 3


def test_companyworld_display_by_user(client):
    response = client.get(reverse('companyworld-detail', args=[3]))
    assert response.status_code == 401


def test_companyworld_create_by_admin(admin_client):
    data = {
        'company': 5,
        "swift": '8111111111_',
    }
    url = reverse('companyworld-list')
    response = admin_client.post(
        url, data=json.dumps(data), content_type="application/json")
    response_json = response.json()

    assert response_json['company'] == [
        'Invalid pk "5" - object does not exist.'
    ]
    assert response_json['swift'] == ['Enter a valid integer.']

    data = {'company': 2, "swift": '12222222222222222222'}

    response = admin_client.post(
        url, data=json.dumps(data), content_type="application/json")
    response_json = response.json()
    assert response.status_code == 201
    assert response_json['company'] == 2
    assert response_json['swift'] == '12222222222222222222'


def test_companyworld_update_world_by_admin(admin_client):
    data = {'swift': '12222222222222222222'}
    url = reverse('companyworld-detail', args=[3])
    response = admin_client.patch(
        url, data=json.dumps(data), content_type="application/json")
    response_json = response.json()

    assert response.status_code == 200
    assert response_json['swift'] == '12222222222222222222'
