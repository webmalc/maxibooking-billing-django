import arrow
import pytest
import stripe
from django.conf import settings
from django.core.urlresolvers import reverse

from billing.lib.test import json_contains
from finances.models import Order

pytestmark = pytest.mark.django_db


def test_payment_system_list_by_user(client):
    response = client.get(reverse('payment-systems-list'))
    assert response.status_code == 401


def test_payment_system_list_by_admin(admin_client):
    response = admin_client.get(reverse('payment-systems-list'))
    assert response.status_code == 200
    assert len(response.json()) == 3
    json_contains(response, 'bill')
    json_contains(response, 'rbk')
    json_contains(response, 'stripe')


def test_payment_system_list_filtered_by_admin(admin_client, make_orders):
    response = admin_client.get(reverse('payment-systems-list') + '?order=1')
    assert response.status_code == 200
    assert len(response.json()) == 1
    json_contains(response, 'stripe')


def test_payment_system_without_order_display_by_admin(admin_client,
                                                       make_orders):
    response = admin_client.get(
        reverse('payment-systems-detail', args=('rbk', )))
    assert response.status_code == 200
    response_json = response.json()
    response_json['id'] = 'rbk'
    assert 'Invalid request' in response_json['html']


def test_payment_system_display_by_admin(admin_client, make_orders):
    response = admin_client.get(
        reverse('payment-systems-detail', args=('stripe', )) + '?order=1')
    assert response.status_code == 200
    response_json = response.json()
    assert 'html' in response_json
    response_json['id'] = 'stripe'


def test_rbk_display_by_admin(admin_client, make_orders):
    response = admin_client.get(
        reverse('payment-systems-detail', args=('rbk', )) + '?order=5')
    assert response.status_code == 200
    html = response.json()['html']
    assert settings.RBK_SHOP_ID in html
    assert 'order #5' in html
    assert '2500.50' in html
    assert 'RUR' in html
    assert '1571bad0f3b71baf0f12e5e146818e2ec7e1c618feb4280116af5d6cf6e78657ed\
a67e6c22e4af02099ba91643d87bfe2d23041e4d038035fb37d573bd19524f' in html


def test_rbk_response(client, make_orders, mailoutbox):
    url = reverse('finances:payment-system-response', args=('rbk', ))
    response = client.post(url)
    assert response.status_code == 400
    assert response.content == b'Bad request.'

    data = {
        'orderId': '5',
        'eshopId': '1',
        'serviceName': '2',
        'recipientAmount': '1300',
        'recipientCurrency': 'EUR',
        'paymentStatus': '1',
        'userName': 'user-seven',
        'userEmail': 'user@seven.com',
        'paymentData': '2017-09-09 12:12:12',
        'hash': 'qwerty',
    }
    response = client.post(url, data)
    assert response.status_code == 400
    assert response.content == b'Invalid payment status != 5.'

    data['paymentStatus'] = '5'
    response = client.post(url, data)
    assert response.status_code == 400
    assert response.content == b'Invalid signature.'

    data['hash'] = '152f9d7063adcc208ec46353f6ae247b6dff0ce9a7e5779eeaaff44e5b\
5f26f8e6bc4647a51228ec0de4258a60fd645a1d4b360a7942835c1f29492745eb68bc'

    response = client.post(url, data)
    assert response.status_code == 400
    assert response.content == b'Invalid currency.'

    data['recipientCurrency'] = 'RUR'
    data['hash'] = 'd68c3a1e5f0efd9db52f6cdff8a28cff24bacd134145c951623915418a\
a68cdb375ce1e438200b122f1a5146be7a57a33ae7dc1be6044a67684446cb34c9d62a'

    response = client.post(url, data)
    assert response.status_code == 400
    assert response.content == b'Invalid payment amount.'

    data['recipientAmount'] = '2500.50'
    data['hash'] = '0d43b84509dcbf1e1b08ad12670a7e66fe8ea5ec2a1c50714e4a7dd284\
c1d3c0dc88bfb22d2d5ed68c2f4128e726d7ad1ed12c2b50159440358e06371368d739'

    response = client.post(url, data)
    assert response.status_code == 200
    assert response.content == b'OK'

    order = Order.objects.get(pk=5)
    now = arrow.now().datetime
    format = '%d.%m.%Y %H:%I'
    assert order.status == 'paid'
    assert order.payment_system == 'rbk'
    assert order.paid_date.strftime(format) == now.strftime(format)
    assert order.transactions.first().data == data

    mail = mailoutbox[-1]
    assert mail.recipients() == [order.client.email]
    assert 'Your payment was successful' in mail.subject


def test_stripe_display_by_admin(admin_client, make_orders):
    response = admin_client.get(
        reverse('payment-systems-detail', args=('stripe', )) + '?order=4')
    assert response.status_code == 200
    html = response.json()['html']
    assert settings.STRIPE_PUBLISHABLE_KEY in html
    assert 'order #4' in html
    assert '12500' in html
    assert 'eur' in html


def test_stripe_response(client, make_orders, mailoutbox, mocker):
    url = reverse('finances:payment-system-response', args=('stripe', ))
    response = client.post(url)
    assert response.status_code == 400
    assert response.content == b'Bad request.'

    data = {
        'order_id': 1111,
        'stripeToken': 'stripe_token',
        'stripeEmail': 'invalid_email',
    }
    response = client.post(url, data)
    assert response.status_code == 400
    assert response.content == b'Order #1111 not found.'

    data['order_id'] = 4
    response = client.post(url, data)
    assert response.status_code == 400
    assert response.content == b'Invalid client email.'

    data['stripeEmail'] = 'user@one.com'
    customer = stripe.Customer()
    customer.id = 'test_id'
    mock_data = {'test': 'test_charge'}
    stripe.Customer.create = mocker.MagicMock(return_value=customer)
    stripe.Charge.create = mocker.MagicMock(return_value=mock_data)
    response = client.post(url, data)

    assert response.status_code == 302
    assert response.url == settings.MB_SITE_URL

    order = Order.objects.get(pk=4)
    now = arrow.now().datetime
    format = '%d.%m.%Y %H:%I'
    assert order.status == 'paid'
    assert order.payment_system == 'stripe'
    assert order.paid_date.strftime(format) == now.strftime(format)
    assert order.transactions.first().data == mock_data

    mail = mailoutbox[-1]
    assert mail.recipients() == [order.client.email]
    assert 'Your payment was successful' in mail.subject


def test_bill_display_by_admin(admin_client, make_orders):
    response = admin_client.get(
        reverse('payment-systems-detail', args=('bill', )) + '?order=5')
    assert response.status_code == 200
    html = response.json()['html']
    assert 'Счет №5' in html
    assert 'Две тысячи пятьсот рублей, пятьдесят копеек' in html
