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
