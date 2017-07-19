import json

from django.core.urlresolvers import reverse

from billing.lib.test import json_contains


# Properties tests


def test_properties_list_by_user(client):
    response = client.get(reverse('property-list'))
    assert response.status_code == 401


def test_properties_list_by_admin(admin_client):
    response = admin_client.get(reverse('property-list'))
    assert response.status_code == 200
    assert len(response.json()['results']) == 3
    json_contains(response, 'Hotel two')


def test_property_display_by_admin(admin_client):
    response = admin_client.get(reverse('property-detail', args=[3]))
    assert response.status_code == 200
    json_contains(response, 'Hotel three')


def test_property_display_by_user(client):
    response = client.get(reverse('property-detail', args=[3]))
    assert response.status_code == 401


def test_property_create_invalid_by_admin(admin_client):
    data = json.dumps({'name': '1'})
    response = admin_client.post(
        reverse('property-list'), data=data, content_type="application/json")
    response_json = response.json()

    assert response_json[
        'name'] == ['Ensure this field has at least 2 characters.']
    assert response_json['city'] == ['This field is required.']
    assert response_json['client'] == ['This field is required.']


def test_property_create_by_admin(admin_client):
    data = json.dumps({
        'name': 'new test property',
        'city': 1,
        'client': 'user-one'
    })
    response = admin_client.post(
        reverse('property-list'), data=data, content_type="application/json")
    response_json = response.json()

    assert response_json['name'] == 'new test property'
    assert response_json['created_by'] == 'admin'

    response = admin_client.get(reverse('property-list'))
    assert len(response.json()['results']) == 4
    json_contains(response, 'new test property')


# Countries tests


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


# Regions tests


def test_region_list_by_user(client):
    response = client.get(reverse('region-list'))
    assert response.status_code == 401


def test_regions_list_by_admin(admin_client):
    response = admin_client.get(reverse('region-list'))
    assert response.status_code == 200
    assert len(response.json()['results']) == 7
    json_contains(response, 'Masvingo')


def test_regions_display_by_admin(admin_client):
    response = admin_client.get(reverse('region-detail', args=[3]))
    assert response.status_code == 200
    json_contains(response, 'Mashonaland East')


def test_regions_display_by_user(client):
    response = client.get(reverse('region-detail', args=[3]))
    assert response.status_code == 401


# Cities tests


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
