import json

from django.urls import reverse

from billing.lib.test import json_contains


def test_companies_list_by_user(client):
    response = client.get(reverse('company-list'))
    assert response.status_code == 401


def test_companies_list_by_admin(admin_client):
    response = admin_client.get(reverse('company-list'))
    assert response.status_code == 200
    assert len(response.json()['results']) == 3
    json_contains(response, 'company en')


def test_companies_display_by_admin(admin_client):
    response = admin_client.get(reverse('company-detail', args=[2]))
    assert response.status_code == 200
    response_json = response.json()
    response_json['name'] = 'company ru'
    assert 'en/companies-ru/2/' in response_json['ru']

    response = admin_client.get(reverse('company-detail', args=[3]))
    assert response.status_code == 200
    response_json = response.json()
    assert response_json['name'] == 'company en'
    assert 'en/companies-world/3/' in response_json['world']


def test_company_display_by_user(client):
    response = client.get(reverse('company-detail', args=[1]))
    assert response.status_code == 401


def test_company_create_by_admin(admin_client):
    data = {
        'name': 'test',
        'client': 'invalid-user',
        'city': 1,
        'region': 1,
        'address': '1212',
        'postal_code': '12121212121212',
        'account_number': '123322323232323',
        'bank': 'bank'
    }
    url = reverse('company-list')
    response = admin_client.post(
        url, data=json.dumps(data), content_type="application/json")
    response_json = response.json()

    assert response_json['client'] == [
        'Object with login=invalid-user does not exist.'
    ]
    data['client'] = 'user-one'
    response = admin_client.post(
        url, data=json.dumps(data), content_type="application/json")
    response_json = response.json()
    assert response.status_code == 201
    assert response_json['name'] == 'test'
    assert response_json['bank'] == 'bank'
    assert response_json['account_number'] == '123322323232323'


# def test_company_create_ru_by_admin(admin_client):
#     data = {
#         'name': 'test',
#         'client': 'invalid-user',
#         'city': 1,
#         'region': 1,
#         'address': '1212',
#         'postal_code': '12121212121212',
#         'account_number': '123322323232323',
#         'bank': 'bank',
#         'ru': {
#             'form': 'ooo',
#             'ogrn': 1,
#             'inn': 1,
#             'kpp': 1,
#             'bik': 1,
#             'corr_account': 1,
#             'boss_firstname': '123123',
#             'boss_lastname': 'sdfsdfsdfsdf',
#             'boss_patronymic': '123123',
#             'boss_operation_base': 'charter',
#             'proxy_number': '123123',
#             'proxy_date': '2017-11-28T13:28:08Z'
#         }
#     }
#     url = reverse('company-list')
#     response = admin_client.post(
#         url, data=json.dumps(data), content_type="application/json")
#     response_json = response.json()

#     assert response_json['client'] == [
#         'Object with login=invalid-user does not exist.'
#     ]
#     assert response_json['ru']['ogrn'] == [
#         'Ensure this field has at least 13 characters.'
#     ]
#     assert response_json['ru']['inn'] == [
#         'Ensure this field has at least 10 characters.'
#     ]
#     assert response_json['ru']['kpp'] == [
#         'Ensure this field has at least 9 characters.'
#     ]
#     assert response_json['ru']['corr_account'] == [
#         'Ensure this field has at least 20 characters.'
#     ]
#     assert response_json['ru']['bik'] == [
#         'Ensure this field has at least 7 characters.'
#     ]

#     data['client'] = 'user-one'
#     data['ru']['ogrn'] = '1' * 13
#     data['ru']['inn'] = '1' * 10
#     data['ru']['kpp'] = '1' * 9
#     data['ru']['corr_account'] = '1' * 20
#     data['ru']['bik'] = '1' * 7
#     response = admin_client.post(
#         url, data=json.dumps(data), content_type="application/json")
#     response_json = response.json()
#     assert response.status_code == 201
#     assert response_json['name'] == 'test'
#     assert response_json['ru']['ogrn'] == '1' * 13
#     assert response_json['ru']['boss_firstname'] == '123123'


def test_company_update_by_admin(admin_client):
    data = {
        'name': 'updated',
    }
    url = reverse('company-detail', args=[3])
    response = admin_client.patch(
        url, data=json.dumps(data), content_type="application/json")
    response_json = response.json()

    assert response.status_code == 200
    assert response_json['name'] == 'updated'
