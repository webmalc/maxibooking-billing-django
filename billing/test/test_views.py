from django.core.urlresolvers import reverse

from billing.lib.test import json_contains


def test_admin_view_by_admin(admin_client):
    response = admin_client.get(reverse('admin:index'))
    assert response.status_code == 200


def test_admin_view_by_user(client):
    response = client.get(reverse('admin:index'))
    assert response.status_code == 302


def test_main_view_by_user(client):
    response = client.get(reverse('api-root'))
    assert response.status_code == 401


def test_main_view_by_admin(admin_client):
    response = admin_client.get(reverse('api-root'))
    assert response.status_code == 200
    json_contains(response, '/en/countries')


def test_main_view_by_admin_ru(admin_client, settings):
    settings.LANGUAGE_CODE = 'ru'
    response = admin_client.get(reverse('api-root'))
    assert response.status_code == 200
    json_contains(response, '/ru/countries')
    json_contains(response, '/ru/regions')
    json_contains(response, '/ru/cities')
