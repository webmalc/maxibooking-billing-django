from django.core.urlresolvers import reverse

from billing.lib.test import json_contains


def test_price_list_by_user(client):
    response = client.get(reverse('price-list'))
    assert response.status_code == 401


def test_price_list_by_admin(admin_client, settings):
    response = admin_client.get(reverse('price-list'))
    assert response.status_code == 200
    assert len(response.json()['results']) == 4
    json_contains(response, '234234.00')


def test_price_display_by_admin(admin_client):
    response = admin_client.get(reverse('price-detail', args=[7]))
    assert response.status_code == 200
    response_json = response.json()
    assert response_json['price'] == '2300.00'
    assert response_json['country'] == 'ad'


def test_price_display_by_user(client):
    response = client.get(reverse('price-detail', args=[7]))
    assert response.status_code == 401
