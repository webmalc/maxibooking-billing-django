import json

from django.urls import reverse
from moneyed import Money

from billing.lib.test import json_contains
from clients.models import Client
from hotels.models import Room


def test_rooms_list_by_user(client):
    response = client.get(reverse('room-list'))
    assert response.status_code == 401


def test_rooms_list_by_admin(admin_client):
    response = admin_client.get(reverse('room-list'))
    assert response.status_code == 200
    assert len(response.json()['results']) == 3
    json_contains(response, 'Room two')


def test_rooms_display_by_admin(admin_client):
    response = admin_client.get(reverse('room-detail', args=[3]))
    assert response.status_code == 200
    json_contains(response, 'Room three')


def test_room_display_by_user(client):
    response = client.get(reverse('room-detail', args=[3]))
    assert response.status_code == 401


def test_room_create_invalid_by_admin(admin_client):
    data = json.dumps({'name': '1', 'rooms': 'invalid'})
    response = admin_client.post(
        reverse('room-list'), data=data, content_type="application/json")
    response_json = response.json()

    assert response_json['name'] == [
        'Ensure this field has at least 2 characters.'
    ]
    assert response_json['rooms'] == ['A valid integer is required.']
    assert response_json['property'] == ['This field is required.']


def test_room_create_by_admin(admin_client):
    """
    Test rooms creating via the REST endpoint
    """
    data = json.dumps({
        'name': 'new test room',
        'property': 1,
        'rooms': 23,
        'max_occupancy': 3,
        'price': 12.55,
        'price_currency': 'GIP',
        'client': 'user-one'
    })
    response = admin_client.post(
        reverse('room-list'), data=data, content_type="application/json")
    response_json = response.json()

    assert response_json['name'] == 'new test room'
    assert response_json['rooms'] == 23
    assert response_json['created_by'] == 'admin'
    assert response_json['max_occupancy'] == 3
    assert response_json['price'] == '12.55'
    assert response_json['price_currency'] == 'GIP'
    assert Room.objects.all().first().price == Money(12.55, 'GIP')

    response = admin_client.get(reverse('room-list'))
    assert len(response.json()['results']) == 4


def test_room_create_without_price_by_admin(admin_client):
    """
    Test rooms creating via the REST endpoint (with the default price)
    """
    data = json.dumps({
        'name': 'new test room',
        'property': 1,
        'rooms': 23,
        'max_occupancy': 3,
        'client': 'user-one'
    })
    response = admin_client.post(
        reverse('room-list'), data=data, content_type="application/json")
    response_json = response.json()

    assert response_json['price'] == '0.00'
    assert response_json['price_currency'] == 'EUR'
    assert Room.objects.all().first().price == Money(0, 'EUR')


def test_rooms_count(admin_client):
    assert Room.objects.count_rooms(Client.objects.get(pk=1)) == 57
