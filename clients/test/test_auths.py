import pytest
from django.core.urlresolvers import reverse

from billing.lib.test import json_contains

pytestmark = pytest.mark.django_db


def test_clients_auth_list_by_user(client):
    response = client.get(reverse('clientauth-list'))
    assert response.status_code == 401


def test_clients_auth_list_by_admin(admin_client):
    response = admin_client.get(reverse('clientauth-list'))
    assert response.status_code == 200
    assert len(response.json()['results']) == 3
    json_contains(response, '127.0.0.1')


def test_client_auth_display_by_user(client):
    response = client.get(reverse('clientauth-detail', args=['1']))
    assert response.status_code == 401


def test_client_auth_display_by_admin(admin_client):
    response = admin_client.get(reverse('clientauth-detail', args=['3']))
    assert response.status_code == 200
    json_contains(response, 'user_agent 2')


# def test_client_auth_create_by_admin(admin_client):
#     data = json.dumps({
#         'login': 'new-user',
#         'email': 'new@user.mail',
#         'name': 'New User',
#         'phone': '+79239999999',
#         'country': 'af',
#         'postal_code': '123456',
#         'address': 'test address',
#         'ru': {
#             'passport_serial': '1' * 4,
#             'passport_number': '1' * 6,
#             'passport_date': '2017-12-01T10:22:48.995041Z',
#             'passport_issued_by': 'issued by',
#             'inn': '1' * 10,
#         }
#     })
#     response = admin_client.post(
#         reverse('clientauth-list'), data=data,
# content_type="application/json")
#     response_json = response.json()

#     assert response_json['login'] == 'new-user'
#     assert response_json['status'] == 'not_confirmed'
#     assert response_json['created_by'] == 'admin'
#     assert response_json['postal_code'] == '123456'
#     assert response_json['address'] == 'test address'
#     assert response_json['ru']['passport_serial'] == '1111'

#     response = admin_client.get(reverse('client-list'))
#     assert len(response.json()['results']) == 8
#     json_contains(response, 'new@user.mail')
