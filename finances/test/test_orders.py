import arrow
import pytest
from django.conf import settings
from django.core.urlresolvers import reverse

from billing.lib.test import json_contains
from clients.tasks import client_services_update

from ..models import Order
from ..tasks import orders_payment_notify

pytestmark = pytest.mark.django_db


@pytest.fixture()
def make_orders():
    now = arrow.utcnow()
    order = Order()
    order.client_id = 1
    order.price = 12500.00
    order.status = 'new'
    order.note = 'payment notification'
    order.expired_date = now.shift(days=2).datetime
    order.save()

    order.pk = None
    order.status = 'paid'
    order.note = 'paid order'
    order.save()

    order.pk = None
    order.status = 'new'
    order.note = 'order expired'
    order.expired_date = now.shift(days=-1).datetime
    order.save()

    order.pk = None
    order.status = 'new order'
    order.note = None
    order.expired_date = now.shift(days=5).datetime

    return None


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


def test_manager_get_for_payment_notification(make_orders):
    orders = Order.objects.get_for_payment_notification()
    assert orders.count() == 1
    assert orders[0].note == 'payment notification'
    assert orders[0].status in ('new', 'processing')
    assert orders[0].expired_date <= arrow.utcnow().shift(
        days=settings.MB_ORDER_PAYMENT_NOTIFY_DAYS).datetime


def test_orders_payment_notification(make_orders, mailoutbox):
    orders_payment_notify.delay()
    mailoutbox = [m for m in mailoutbox if "will expire soon" in m.subject]
    assert len(mailoutbox) == 1
    assert mailoutbox[0].recipients() == ['user@one.com']


def test_manager_get_expired(make_orders):
    orders = Order.objects.get_expired()
    assert orders.count() == 1
    assert orders[0].note == 'order expired'
    assert orders[0].status in ('new', 'processing')
    assert orders[0].expired_date > arrow.utcnow()
