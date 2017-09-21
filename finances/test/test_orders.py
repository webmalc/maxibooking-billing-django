import arrow
import pytest
from django.conf import settings
from django.core.urlresolvers import reverse

from billing.lib.test import json_contains
from clients.tasks import client_services_update

from ..models import Order

pytestmark = pytest.mark.django_db


def test_order_creation_and_modifications(mailoutbox):
    order = Order()
    order.client_id = 1
    order.save()
    assert order.price == 0
    assert order.status == 'new'
    expired_date = arrow.get(order.created).shift(
        days=+settings.MB_ORDER_EXPIRED_DAYS).floor('second').datetime
    assert arrow.get(order.expired_date).floor('second') == expired_date

    assert len(mailoutbox) == 1
    mail = mailoutbox[0]
    assert 'New order created' in mail.subject
    assert mail.recipients() == ['user@one.com']

    order.client_services.add(1, 2)
    assert float(order.price) == 14001.83
    assert 'Test service two' in order.note
    assert '1999.98' in order.note

    order.note = 'test note'
    order.price = 111.25
    order.save()

    assert float(order.price) == 111.25
    assert order.note == 'test note'

    order.note = None
    order.price = 0
    order.save()
    assert float(order.price) == 14001.83
    assert 'Test service one' in order.note
    assert '12001.85' in order.note


def test_ordrers_list_by_user(client):
    response = client.get(reverse('order-list'))
    assert response.status_code == 401


def test_order_list_by_admin(admin_client):
    client_services_update.delay()
    response = admin_client.get(reverse('order-list'))
    assert response.status_code == 200
    assert len(response.json()['results']) == 3
    json_contains(response, 'Test service one 24664.00')
    json_contains(response, 'Test service one 4600.00')

    response = admin_client.get(
        reverse('order-list') + '?client__login=user-one')
    response_json = response.json()
    assert len(response_json['results']) == 1
    assert response_json['results'][0]['client'] == 'user-one'


def test_order_display_by_user(client):
    client_services_update.delay()
    response = client.get(reverse('order-detail', args=[2]))
    assert response.status_code == 401


def test_order_display_by_admin(admin_client):
    client_services_update.delay()
    response = admin_client.get(reverse('order-detail', args=[2]))
    assert response.status_code == 200
    json_contains(response, 'user-two')
    json_contains(response, '468468.00')
