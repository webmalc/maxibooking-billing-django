import json

from django.core.urlresolvers import reverse

from billing.lib.test import json_contains

from ..models import Client


# Clients tests


def test_clients_list_by_user(client):
    response = client.get(reverse('client-list'))
    assert response.status_code == 401


def test_clients_list_by_admin(admin_client):
    response = admin_client.get(reverse('client-list'))
    assert response.status_code == 200
    assert len(response.json()['results']) == 4
    json_contains(response, 'User Two')


def test_client_display_by_admin(admin_client):
    response = admin_client.get(reverse('client-detail', args=['user-three']))
    assert response.status_code == 200
    json_contains(response, 'user@three.com')


def test_client_display_by_user(client):
    response = client.get(reverse('client-detail', args=['user-three']))
    assert response.status_code == 401


def test_client_create_invalid_by_admin(admin_client):
    data = json.dumps({'login': 'invalid login', 'email': 'user@one.com'})
    response = admin_client.post(
        reverse('client-list'), data=data, content_type="application/json")
    response_json = response.json()

    assert response_json['login'] == [
        'Enter a valid login. This value may \
contain only lowercase letters, numbers, and "-" character.'
    ]
    assert response_json[
        'email'] == ['client with this e-mail already exists.']
    assert response_json['phone'] == ['This field is required.']


def test_client_create_by_admin(admin_client):
    data = json.dumps({
        'login': 'new-user',
        'email': 'new@user.mail',
        'name': 'New User',
        'phone': '+79239999999'
    })
    response = admin_client.post(
        reverse('client-list'), data=data, content_type="application/json")
    response_json = response.json()

    assert response_json['login'] == 'new-user'
    assert response_json['status'] == 'not_confirmed'
    assert response_json['created_by'] == 'admin'

    response = admin_client.get(reverse('client-list'))
    assert len(response.json()['results']) == 5
    json_contains(response, 'new@user.mail')


def test_client_confirm_by_user(client):
    response = client.post(
        reverse('client-confirm', args=['new-user']),
        content_type="application/json")
    assert response.status_code == 401


def test_client_confirm_by_admin(admin_client):
    response = admin_client.post(
        reverse('client-confirm', args=['user-three']),
        content_type="application/json")

    assert response.json()['status'] is True
    client = Client.objects.get(login='user-three')
    assert client.status == 'active'
