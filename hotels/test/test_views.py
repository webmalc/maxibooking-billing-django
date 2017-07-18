import json

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
    assert response.status_code == 401


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
    assert response.status_code == 401


def test_property_create_invalid_by_admin(admin_client):
    data = json.dumps({'name': '1'})
    response = admin_client.post(
        reverse('hotels:property-list'),
        data=data,
        content_type="application/json")
    response_json = response.json()

    assert response_json[
        'name'] == ['Ensure this field has at least 2 characters.']
    assert response_json['city'] == ['This field is required.']


def test_property_create_by_admin(admin_client):
    data = json.dumps({'name': 'new test client', 'city': 1})
    response = admin_client.post(
        reverse('hotels:property-list'),
        data=data,
        content_type="application/json")
    response_json = response.json()

    assert response_json['name'] == 'new test client'
    assert response_json['created_by'] == 'admin'

    response = admin_client.get(reverse('hotels:property-list'))
    assert len(response.json()['results']) == 4
    json_contains(response, 'new test client')


# Countries tests


def test_countries_list_by_user(client):
    response = client.get(reverse('hotels:country-list'))
    assert response.status_code == 401


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
    assert response.status_code == 401


# Regions tests


def test_region_list_by_user(client):
    response = client.get(reverse('hotels:region-list'))
    assert response.status_code == 401


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
    assert response.status_code == 401


# Cities tests


def test_cities_list_by_user(client):
    response = client.get(reverse('hotels:city-list'))
    assert response.status_code == 401


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
    assert response.status_code == 401
