import json

from django.core.urlresolvers import reverse

from billing.lib.test import json_contains


def test_companyru_list_by_user(client):
    response = client.get(reverse('companyru-list'))
    assert response.status_code == 401


def test_companyru_list_by_admin(admin_client):
    response = admin_client.get(reverse('companyru-list'))
    assert response.status_code == 200
    assert len(response.json()['results']) == 1

    json_contains(response, 'boss firstname')
    json_contains(response, 'boss lastname')
    json_contains(response, '222222222')
    json_contains(response, 'charter')


def test_companyru_display_by_admin(admin_client):
    response = admin_client.get(reverse('companyru-detail', args=[2]))
    assert response.status_code == 200
    response_json = response.json()
    response_json['kpp'] = '222222222'
    response_json['ogrn'] = '1222222222221'


def test_companyru_display_by_user(client):
    response = client.get(reverse('companyru-detail', args=[2]))
    assert response.status_code == 401


def test_companyru_create_by_admin(admin_client):
    data = {
        'form': 'ooo',
        'ogrn': 1,
        'inn': 1,
        'kpp': 1,
        'bik': 1,
        'corr_account': 1,
        'boss_firstname': '123123',
        'boss_lastname': 'sdfsdfsdfsdf',
        'boss_patronymic': '123123',
        'boss_operation_base': 'proxy',
        # 'proxy_number': '123123',
        # 'proxy_date': '2017-11-28T13:28:08Z'
    }
    url = reverse('companyru-list')
    response = admin_client.post(
        url, data=json.dumps(data), content_type="application/json")
    response_json = response.json()

    assert response_json['company'] == ['This field is required.']
    assert response_json['ogrn'] == [
        'Ensure this field has at least 13 characters.'
    ]
    assert response_json['inn'] == [
        'Ensure this field has at least 10 characters.'
    ]
    assert response_json['kpp'] == [
        'Ensure this field has at least 9 characters.'
    ]
    assert response_json['corr_account'] == [
        'Ensure this field has at least 20 characters.'
    ]
    assert response_json['bik'] == [
        'Ensure this field has at least 7 characters.'
    ]
    data['company'] = 1
    data['ogrn'] = '1' * 13
    data['inn'] = '1' * 10
    data['kpp'] = '1' * 9
    data['corr_account'] = '1' * 20
    data['bik'] = '1' * 7
    response = admin_client.post(
        url, data=json.dumps(data), content_type="application/json")
    response_json = response.json()

    assert response_json['non_field_errors'] == [
        'Please fill a proxy date and a proxy number.'
    ]
    data.update({
        'proxy_number': '123123',
        'proxy_date': '2017-11-28T13:28:08Z'
    })

    response = admin_client.post(
        url, data=json.dumps(data), content_type="application/json")
    response_json = response.json()
    assert response.status_code == 201
    assert response_json['ogrn'] == '1' * 13
    assert response_json['company'] == 1
    assert response_json['boss_firstname'] == '123123'


def test_companyru_update_world_by_admin(admin_client):
    data = {'ogrn': '1111111111111'}
    url = reverse('companyru-detail', args=[2])
    response = admin_client.patch(
        url, data=json.dumps(data), content_type="application/json")
    response_json = response.json()

    assert response.status_code == 200
    assert response_json['ogrn'] == '1111111111111'
