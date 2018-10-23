import json

from django.core.urlresolvers import reverse

from billing.lib.test import json_contains

from ..models import ClientWebsite


def test_websites_list_by_user(client):
    response = client.get(reverse('clientwebsite-list'))
    assert response.status_code == 401


def test_websites_list_by_admin(admin_client):
    response = admin_client.get(reverse('clientwebsite-list'))
    assert response.status_code == 200
    assert len(response.json()['results']) == 7
    json_contains(response, 'https://user-rus.maaaxi.com')


def test_websites_display_by_admin(admin_client):
    response = admin_client.get(
        reverse('clientwebsite-detail', args=['user-one']))
    assert response.status_code == 200
    response_json = response.json()
    assert response_json['url'] == 'https://user-one.maaaxi.com'
    assert response_json['is_enabled'] is True


def test_websites_display_by_user(client):
    response = client.get(reverse('clientwebsite-detail', args=['user-one']))
    assert response.status_code == 401


def test_websites_create_by_admin(admin_client):
    data = {
        'client': 'invalid-user',
        'url': 'https://user-one.maaaxi.com',
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
    assert response.status_code == 400
    assert response_json['non_field_errors'] == [
        'This client already has a website'
    ]

    ClientWebsite.objects.filter(client__login='user-four').delete()
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
