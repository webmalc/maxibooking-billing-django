import arrow
import pytest
from django.conf import settings
from django.core.urlresolvers import reverse
from moneyed import EUR, RUB, Money

from billing.lib.test import json_contains
from clients.models import Client
from clients.tasks import client_services_update

from ..models import Order
from ..tasks import orders_clients_disable, orders_payment_notify

pytestmark = pytest.mark.django_db


def test_order_creation_and_modifications(mailoutbox):
    order = Order()
    order.client_id = 1
    order.save()
    assert order.price == Money(0, EUR)
    assert order.status == 'new'
    expired_date = arrow.get(order.created).shift(
        days=+settings.MB_ORDER_EXPIRED_DAYS).floor('second').datetime
    assert arrow.get(order.expired_date).floor('second') == expired_date

    assert len(mailoutbox) == 1
    mail = mailoutbox[0]
    assert 'New order created' in mail.subject
    assert mail.recipients() == ['user@one.com']

    order.client_services.add(1, 2)
    assert order.price == Money(14001.83, EUR)
    assert 'Test service two' in order.note
    assert '1,999.98' in order.note

    order.note = 'test note'
    order.price = Money(111.25, EUR)
    order.save()

    assert order.price == Money(111.25, EUR)
    assert order.note == 'test note'

    order.note = None
    order.price = 0
    order.save()
    assert order.price == Money(14001.83, EUR)
    assert 'Test service one' in order.note
    assert '12,001.85' in order.note


def test_ordrers_list_by_user(client):
    response = client.get(reverse('order-list'))
    assert response.status_code == 401


def test_order_list_by_admin(admin_client):
    client_services_update.delay()
    response = admin_client.get(reverse('order-list'))
    assert response.status_code == 200
    assert len(response.json()['results']) == 3
    json_contains(response, 'Test service one 24,664.00')
    json_contains(response, 'Test service one 4,600.00')

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
    json_contains(response, '468,468.00')


def test_manager_get_for_payment_notification(make_orders):
    orders = Order.objects.get_for_payment_notification()
    assert orders.count() == 1
    assert orders[0].note == 'payment notification'
    assert orders[0].status in ('new', 'processing')
    assert orders[0].expired_date <= arrow.utcnow().shift(
        days=settings.MB_ORDER_PAYMENT_NOTIFY_DAYS).datetime


def test_orders_payment_notification(make_orders, mailoutbox):
    orders_payment_notify.delay()
    mailoutbox = [m for m in mailoutbox if 'will expire soon' in m.subject]
    assert len(mailoutbox) == 1
    assert mailoutbox[0].recipients() == ['user@one.com']


def test_manager_get_expired(make_orders):
    orders = Order.objects.get_expired()
    assert orders.count() == 1
    assert orders[0].note == 'order expired'
    assert orders[0].status in ('new', 'processing')
    assert orders[0].expired_date <= arrow.utcnow()


def test_orders_clients_disable(make_orders, mailoutbox):
    orders_clients_disable.delay()
    mailoutbox = [m for m in mailoutbox if 'account is disabled' in m.subject]
    assert len(mailoutbox) == 1
    assert mailoutbox[0].recipients() == ['user@one.com']
    client = Client.objects.get(pk=1)
    assert client.status == 'disabled'
    format = '%d.%m.%Y %H:%I'
    assert client.disabled_at.strftime(format) == arrow.utcnow().strftime(
        format)


def test_order_with_invalid_currencies():
    order = Order()
    order.client_id = 1
    order.save()
    assert order.price == Money(0, EUR)
    order.client_services.add(5)
    assert order.price == Money(4000, RUB)
    order.client_services.add(4)
    assert order.status == 'corrupted'
    assert order.price == Money(0, EUR)
