from django.core.management import call_command
from django.core.urlresolvers import reverse
from django.utils.six import StringIO

from billing.lib.test import json_contains
from hotels.models import Country


def test_countries_list_by_user(client):
    response = client.get(reverse('country-list'))
    assert response.status_code == 401


def test_countries_list_by_admin(admin_client):
    response = admin_client.get(reverse('country-list'))
    assert response.status_code == 200
    assert len(response.json()['results']) == 4
    json_contains(response, 'United States')


def test_countries_tld_filter_by_admin(admin_client):
    country = Country()
    country.name = 'test'
    country.name_ascii = 'test'
    country.tld = ''
    country.save()

    response = admin_client.get(reverse('country-list'))
    assert response.status_code == 200
    assert len(response.json()['results']) == 5
    json_contains(response, 'test')

    response = admin_client.get(reverse('country-list') + '?with_tld=true')
    assert response.status_code == 200
    assert len(response.json()['results']) == 4

    response = admin_client.get(reverse('country-list') + '?with_tld=false')
    assert response.status_code == 200
    assert len(response.json()['results']) == 1
    json_contains(response, 'test')


def test_countries_display_by_admin(admin_client):
    response = admin_client.get(reverse('country-detail', args=['ae']))
    assert response.status_code == 200
    json_contains(response, 'United Arab Emirates')


def test_countries_display_by_user(client):
    response = client.get(reverse('country-detail', args=['ae']))
    assert response.status_code == 401


def test_countries_translations(admin_client, settings):
    settings.LANGUAGE_CODE = 'ru'
    response = admin_client.get(reverse('country-detail', args=['ae']))
    assert response.status_code == 200
    assert response.json()['name'] == 'United Arab Emirates'
    call_command('citytranslate', stdout=StringIO())
    response = admin_client.get(reverse('country-detail', args=['ae']))
    assert response.json()['name'] == 'Объединенные Арабские Эмираты'
