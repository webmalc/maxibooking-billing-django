import json

from billing.lib.test import json_contains
from django.core.urlresolvers import reverse


def test_websites_list_by_user(client):
    response = client.get(reverse('clientwebsite-list'))
    assert response.status_code == 401


def test_websites_list_by_admin(admin_client):
    response = admin_client.get(reverse('clientwebsite-list'))
    assert response.status_code == 200
    assert len(response.json()['results']) == 3
    json_contains(response, 'http://hotel.one')


def test_websites_display_by_admin(admin_client):
    response = admin_client.get(
        reverse('clientwebsite-detail', args=['user-one']))
    assert response.status_code == 200
    response_json = response.json()
    response_json['url'] = 'http://user-one.com'
    response_json['is_enabled'] = False


def test_websites_display_by_user(client):
    response = client.get(reverse('clientwebsite-detail', args=['user-one']))
    assert response.status_code == 401


def test_websites_create_by_admin(admin_client):
    data = {
        'client': 'invalid-user',
        'url': 'http://hotel.one',
    }
    url = reverse('clientwebsite-list')
    response = admin_client.post(
        url, data=json.dumps(data), content_type="application/json")
    response_json = response.json()

    assert response_json['client'] == [
        'Object with login=invalid-user does not exist.'
    ]
    assert response_json['url'] == [
        'client website with this url already exists.'
    ]

    data = {
        'client': 'user-four',
        'url': 'http://hotel.two',
    }
    response = admin_client.post(
        url, data=json.dumps(data), content_type="application/json")
    response_json = response.json()
    assert response.status_code == 201
    assert response_json['client'] == 'user-four'
    assert response_json['url'] == 'http://hotel.two'
    assert response_json['is_enabled'] is False


def test_websites_update_world_by_admin(admin_client):
    data = {'url': 'http://new.site'}
    url = reverse('clientwebsite-detail', args=['user-one'])
    response = admin_client.patch(
        url, data=json.dumps(data), content_type="application/json")
    response_json = response.json()

    assert response.status_code == 200
    assert response_json['url'] == 'http://new.site'
