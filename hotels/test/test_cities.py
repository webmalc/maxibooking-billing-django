import json

from django.core.urlresolvers import reverse

from billing.lib.test import json_contains


def test_cities_list_by_user(client):
    response = client.get(reverse('city-list'))
    assert response.status_code == 401


def test_cities_list_by_admin(admin_client):
    response = admin_client.get(reverse('city-list'))
    assert response.status_code == 200
    assert len(response.json()['results']) == 5
    json_contains(response, 'Chegutu')


def test_city_display_by_admin(admin_client):
    response = admin_client.get(reverse('city-detail', args=[3]))
    assert response.status_code == 200
    json_contains(response, 'Bindura')


def test_city_display_by_user(client):
    response = client.get(reverse('city-detail', args=[3]))
    assert response.status_code == 401


def test_city_create_by_admin(admin_client, mailoutbox):
    data = json.dumps({
        'name': 'new test city',
        'display_name': 'new test city',
        'country': 'ad',
        'region': 1,
        'is_checked': False,
        'request_client': 1
    })
    response = admin_client.post(
        reverse('city-list'), data=data, content_type="application/json")
    response_json = response.json()

    assert response_json['name'] == 'new test city'

    response = admin_client.get(reverse('city-list'))
    assert len(response.json()['results']) == 6

    assert len(mailoutbox) == 1
    mail = mailoutbox[0]
    assert mail.recipients() == ['admin@example.com', 'manager@example.com']
    assert 'new test city' in mail.alternatives[0][0]
