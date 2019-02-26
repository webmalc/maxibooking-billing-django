import json

from django.core.management import call_command
from django.urls import reverse
from django.utils.six import StringIO

from billing.lib.test import json_contains
from hotels.models import City


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
        'country': 'us',
        'latitude': '-18.13021',
        'longitude': '30.14074',
        'region': 1,
        'is_checked': False,
        'request_client': 'user-one'
    })
    response = admin_client.post(
        reverse('city-list'), data=data, content_type="application/json")
    response_json = response.json()

    assert response_json['name'] == 'new test city'
    assert response_json['request_client'] == 'user-one'

    response = admin_client.get(reverse('city-list'))
    assert len(response.json()['results']) == 6

    city = City.objects.get(name='new test city')
    assert city.timezone.zone == 'Africa/Harare'

    assert len(mailoutbox) == 1
    mail = mailoutbox[0]
    assert mail.recipients() == ['admin@example.com', 'manager@example.com']
    assert 'new test city' in mail.alternatives[0][0]


def test_city_update_by_admin(admin_client):
    data = json.dumps({
        'name': 'updated title',
        'request_client': None,
    })
    response = admin_client.patch(
        reverse('city-detail', args=[1]),
        data=data,
        content_type="application/json")
    response_json = response.json()
    assert response.status_code == 200
    assert response_json['name'] == 'updated title'


def test_cities_set_timezone_command(admin_client, settings):
    City.objects.filter(pk=1).update(
        timezone=None, latitude=55.91, longitude=37.72)
    call_command('citiesprocess', '--timezone', stdout=StringIO())
    response = admin_client.get(reverse('city-detail', args=[1]))
    assert response.json()['timezone'] == 'Europe/Moscow'
