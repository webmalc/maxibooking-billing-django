import pytest
from django.core.management import call_command
from django.core.urlresolvers import reverse

from billing.lib.test import json_contains


@pytest.fixture(scope='module')
def django_db_setup(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        call_command('loaddata', 'tests/users', 'tests/countries',
                     'tests/regions', 'tests/cities', 'tests/properties')


# Properties tests


def test_properties_list_by_user(client):
    response = client.get(reverse('hotels:property-list'))
    assert response.status_code == 403


def test_properties_list_by_admin(admin_client):
    response = admin_client.get(reverse('hotels:property-list'))
    assert response.status_code == 200
    assert len(response.json()['results']) == 3
    json_contains(response, 'Hotel two')


def test_property_display_by_admin(admin_client):
    response = admin_client.get(reverse('hotels:property-detail', args=[3]))
    assert response.status_code == 200
    json_contains(response, 'Hotel three')


def test_property_display_by_user(client):
    response = client.get(reverse('hotels:property-detail', args=[3]))
    assert response.status_code == 403


# Countries tests


def test_countries_list_by_user(client):
    response = client.get(reverse('hotels:country-list'))
    assert response.status_code == 403


def test_countries_list_by_admin(admin_client):
    response = admin_client.get(reverse('hotels:country-list'))
    assert response.status_code == 200
    assert len(response.json()['results']) == 3
    json_contains(response, 'Andorra')


def test_countries_display_by_admin(admin_client):
    response = admin_client.get(reverse('hotels:country-detail', args=['ae']))
    assert response.status_code == 200
    json_contains(response, 'United Arab Emirates')


def test_countries_display_by_user(client):
    response = client.get(reverse('hotels:country-detail', args=['ae']))
    assert response.status_code == 403


# Regions tests


def test_region_list_by_user(client):
    response = client.get(reverse('hotels:region-list'))
    assert response.status_code == 403


def test_regions_list_by_admin(admin_client):
    response = admin_client.get(reverse('hotels:region-list'))
    assert response.status_code == 200
    assert len(response.json()['results']) == 7
    json_contains(response, 'Masvingo')


def test_regions_display_by_admin(admin_client):
    response = admin_client.get(reverse('hotels:region-detail', args=[3]))
    assert response.status_code == 200
    json_contains(response, 'Mashonaland East')


def test_regions_display_by_user(client):
    response = client.get(reverse('hotels:region-detail', args=[3]))
    assert response.status_code == 403


# Cities tests


def test_cities_list_by_user(client):
    response = client.get(reverse('hotels:city-list'))
    assert response.status_code == 403


def test_cities_list_by_admin(admin_client):
    response = admin_client.get(reverse('hotels:city-list'))
    assert response.status_code == 200
    assert len(response.json()['results']) == 5
    json_contains(response, 'Chegutu')


def test_city_display_by_admin(admin_client):
    response = admin_client.get(reverse('hotels:city-detail', args=[3]))
    assert response.status_code == 200
    json_contains(response, 'Bindura')


def test_city_display_by_user(client):
    response = client.get(reverse('hotels:city-detail', args=[3]))
    assert response.status_code == 403
