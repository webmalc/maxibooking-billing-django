import json

import arrow
from django.core.urlresolvers import reverse

from billing.lib.test import json_contains
from clients.models import ClientService
from clients.tasks import client_services_update
from finances.models import Order, Service


def test_client_services_list_by_user(client):
    response = client.get(reverse('clientservice-list'))
    assert response.status_code == 401


def test_client_services_list_by_admin(admin_client):
    response = admin_client.get(reverse('clientservice-list'))
    assert response.status_code == 200
    assert len(response.json()['results']) == 4
    json_contains(response, '12001.85')


def test_client_service_display_by_admin(admin_client):
    response = admin_client.get(reverse('clientservice-detail', args=[1]))
    assert response.status_code == 200
    json_contains(response, '1999.98')
    json_contains(response, 'user-one')


def test_client_service_display_by_user(client):
    response = client.get(reverse('clientservice-detail', args=[1]))
    assert response.status_code == 401


def test_client_service_create_invalid_by_admin(admin_client):
    data = {
        'quantity': -3,
        'client': 'invalid-user',
        'service': 312,
        'begin': arrow.utcnow().isoformat(),
        'end': arrow.utcnow().shift(days=-3).isoformat()
    }
    response = admin_client.post(
        reverse('clientservice-list'),
        data=json.dumps(data),
        content_type="application/json")
    response_json = response.json()

    assert response_json[
        'quantity'] == ['Ensure this value is greater than or equal to 1.']
    assert response_json[
        'service'] == ['Invalid pk "312" - object does not exist.']
    assert response_json[
        'client'] == ['Object with login=invalid-user does not exist.']

    data['quantity'] = 1
    data['client'] = 'user-one'
    data['service'] = 1
    response = admin_client.post(
        reverse('clientservice-list'),
        data=json.dumps(data),
        content_type="application/json")
    response_json = response.json()

    assert response_json['non_field_errors'] == [
        'The fields client, is_enabled, service must make a unique set.'
    ]

    data['service'] = 3
    response = admin_client.post(
        reverse('clientservice-list'),
        data=json.dumps(data),
        content_type="application/json")
    response_json = response.json()

    assert response_json['non_field_errors'] == ['Please correct dates.']

    data['end'] = arrow.utcnow().shift(months=+3).isoformat()
    response = admin_client.post(
        reverse('clientservice-list'),
        data=json.dumps(data),
        content_type="application/json")
    response_json = response.json()


def test_client_service_create_by_admin(admin_client):
    data = {'quantity': 2, 'client': 'user-one', 'service': 2}
    response = admin_client.post(
        reverse('clientservice-list'),
        data=json.dumps(data),
        content_type="application/json")
    response_json = response.json()

    assert response_json['price'] == '7000.00'
    assert response_json['client'] == 'user-one'
    assert response_json['is_enabled'] is True
    assert response_json['country'] == 'ad'
    assert response_json['status'] == 'active'

    begin = arrow.utcnow()
    end = begin.shift(years=+1)
    format = '%d.%m.%Y %H:%I'
    assert arrow.get(response_json['begin']).datetime.strftime(
        format) == begin.datetime.strftime(format)
    assert arrow.get(response_json['end']).datetime.strftime(
        format) == end.datetime.strftime(format)


def test_client_services_update_task(admin_client):
    end = arrow.utcnow().shift(days=+5)
    service = Service.objects.get(pk=1)
    client_service = ClientService()
    client_service.quantity = 2
    client_service.begin = arrow.utcnow().shift(months=-1).datetime
    client_service.end = end.datetime
    client_service.service = service
    client_service.client_id = 4
    client_service.save()
    assert client_service.price == service.get_price(client=4) * 2
    price = service.prices.get(pk=8)
    price.price = 2500
    price.save()

    client_services_update.delay()
    client_service.refresh_from_db()
    assert client_service.status == 'processing'
    assert client_service.end == end.shift(months=+3).datetime
    assert client_service.price == 5000

    order = Order.objects.get(
        client__pk=4, client_services__pk=client_service.pk)
    assert order.price == 5000
    assert order.status == 'new'
