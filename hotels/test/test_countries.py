from django.core.urlresolvers import reverse

from billing.lib.test import json_contains


def test_countries_list_by_user(client):
    response = client.get(reverse('country-list'))
    assert response.status_code == 401


def test_countries_list_by_admin(admin_client):
    response = admin_client.get(reverse('country-list'))
    assert response.status_code == 200
    assert len(response.json()['results']) == 3
    json_contains(response, 'Andorra')


def test_countries_display_by_admin(admin_client):
    response = admin_client.get(reverse('country-detail', args=['ae']))
    assert response.status_code == 200
    json_contains(response, 'United Arab Emirates')


def test_countries_display_by_user(client):
    response = client.get(reverse('country-detail', args=['ae']))
    assert response.status_code == 401
