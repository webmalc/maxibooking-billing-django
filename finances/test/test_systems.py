import json

import arrow
import braintree
import paypalrestsdk
import pytest
import stripe
from django.conf import settings
from django.urls import reverse

from billing.lib.test import json_contains
from clients.models import Client
from finances.models import Order
from finances.systems import manager
from finances.systems.models import Braintree, Paypal, SberbankRest, Stripe

pytestmark = pytest.mark.django_db


def test_payment_system_list_by_user(client):
    response = client.get(reverse('payment-systems-list'))
    assert response.status_code == 401


def test_payment_system_list_by_admin(admin_client):
    response = admin_client.get(reverse('payment-systems-list'))
    assert response.status_code == 200
    assert len(response.json()) == 8
    json_contains(response, 'stripe')
    json_contains(response, 'braintree')
    json_contains(response, 'paypal')


def test_payment_system_list_filtered_by_admin(admin_client, make_orders):
    response = admin_client.get(reverse('payment-systems-list') + '?order=1')
    assert response.status_code == 200
    assert len(response.json()) == 4
    json_contains(response, 'stripe')
    json_contains(response, 'braintree')
    json_contains(response, 'braintree-subscription')
    json_contains(response, 'paypal')


def test_payment_system_list_with_country_overwrite(
        admin_client,
        make_orders,
        settings,
):
    settings.MB_COUNTRIES_OVERWRITE = {'us': 'ru'}
    response = admin_client.get(reverse('payment-systems-list') + '?order=1')
    assert response.status_code == 200
    assert len(response.json()) == 4
    json_contains(response, 'bill')
    json_contains(response, 'rbk')
    json_contains(response, 'sberbank')
    json_contains(response, 'sberbank-rest')


def test_payment_system_without_order_display_by_admin(admin_client,
                                                       make_orders):
    response = admin_client.get(
        reverse('payment-systems-detail', args=('rbk', )))
    assert response.status_code == 200
    response_json = response.json()
    response_json['id'] = 'rbk'
    assert 'the required information are not filled' in response_json['html']


def test_payment_system_display_by_admin(admin_client, make_orders):
    response = admin_client.get(
        reverse('payment-systems-detail', args=('braintree', )) + '?order=1')
    assert response.status_code == 200
    response_json = response.json()
    assert 'html' in response_json
    response_json['id'] = 'braintree'


def test_rbk_display_by_admin(admin_client, make_orders):
    response = admin_client.get(
        reverse('payment-systems-detail', args=('rbk', )) + '?order=5')
    assert response.status_code == 200
    html = response.json()['html']
    assert settings.RBK_SHOP_ID in html
    assert 'order #5' in html
    assert '2500.50' in html
    assert 'RUR' in html
    assert '460cccb4cd0431b526058776cc9dbd2c7e2f81e0e1f9f86baa2cdf271f70dfcf8b\
6fa90f0f7dc7b4e562bf16ca4e422a1bc0e1165d0774e7e440879f51e12919' in html


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
    assert 'Спасибо за Ваш платеж' in mail.subject


def test_manager_get_braintree(make_orders):
    Client.objects.filter(pk=1).update(country_id=2)
    braintree = manager.get('braintree', Order.objects.get(pk=4))
    assert isinstance(braintree, Braintree)
    assert braintree.braintree.merchant_id == 'braintree_merchant_id'
    assert braintree.braintree.public_key == 'braintree_public_key'
    assert braintree.braintree.private_key == 'braintree_private_key'


def test_manager_get_stripe(make_orders, settings):
    settings.MB_SETTINGS_BY_COUNTRY['STRIPE_PUBLISHABLE_KEY'][
        'ae'] = 'stripe_publishable_key_ae'
    settings.MB_SETTINGS_BY_COUNTRY['STRIPE_SECRET_KEY'][
        'ae'] = 'stripe_secret_key_ae'
    Client.objects.filter(pk=1).update(country_id=2)
    stripe = manager.get('stripe', Order.objects.get(pk=4))
    assert isinstance(stripe, Stripe)
    assert stripe.secret_key == 'stripe_secret_key_ae'


def test_braintree_display_by_admin(admin_client, make_orders):
    response = admin_client.get(
        reverse('payment-systems-detail', args=('braintree', )) + '?order=4')
    assert response.status_code == 200
    html = response.json()['html']
    assert 'invalid_braintree_token' in html
    assert 'name="order_id" value="4"' in html
    assert '12,500.00' in html


def test_braintree_response(client, make_orders, mailoutbox, mocker):
    Client.objects.filter(pk=1).update(url='http://example.com')
    url = reverse('finances:payment-system-response', args=('braintree', ))
    response = client.post(url)
    assert response.status_code == 400
    assert response.content == b'Bad request.'

    data = {
        'order_id': 1111,
        'payment_method_nonce': 'invalid token',
    }
    response = client.post(url, data)
    assert response.status_code == 400
    assert response.content == b'Order #1111 not found.'

    data['order_id'] = 4

    class ResultMock(object):
        def __init__(self):
            self.is_success = True
            self.transaction = TransactionMock()

    class TransactionMock(object):
        def __init__(self):
            self.status = braintree.Transaction.Status.SubmittedForSettlement

        def sale(self, params):
            return ResultMock()

    class GatewayMock(object):
        def __init__(self):
            self.transaction = TransactionMock()

    braintree.BraintreeGateway = mocker.MagicMock(return_value=GatewayMock())

    response = client.post(url, data)

    assert response.status_code == 302
    assert response.url == 'http://example.com/management/online/\
api/payment/success'

    order = Order.objects.get(pk=4)
    now = arrow.now().datetime
    format = '%d.%m.%Y %H:%I'
    assert order.status == 'paid'
    assert order.payment_system == 'braintree'
    assert order.paid_date.strftime(format) == now.strftime(format)
    assert order.transactions.first().data == {
        'status': 'submitted_for_settlement'
    }

    mail = mailoutbox[-1]
    assert mail.recipients() == [order.client.email]
    assert 'Thank you for your payment!' in mail.subject


def _test_stripe_display_by_admin(admin_client, key):
    response = admin_client.get(
        reverse('payment-systems-detail', args=('stripe', )) + '?order=4')
    assert response.status_code == 200
    html = response.json()['html']
    assert key in html
    assert 'order #4' in html
    assert '12500' in html
    assert 'eur' in html


def test_stripe_display_by_admin(admin_client, make_orders):
    _test_stripe_display_by_admin(admin_client, 'stripe_publishable_key_all')


def test_stripe_display_ae_by_admin(admin_client, make_orders, settings):
    settings.MB_SETTINGS_BY_COUNTRY['STRIPE_PUBLISHABLE_KEY'][
        'ae'] = 'stripe_publishable_key_ae'
    settings.MB_SETTINGS_BY_COUNTRY['STRIPE_SECRET_KEY'][
        'ae'] = 'stripe_secret_key_ae'
    Client.objects.filter(pk=1).update(country_id=2)
    _test_stripe_display_by_admin(admin_client, 'stripe_publishable_key_ae')


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
    assert 'Thank you for your payment!' in mail.subject


def test_bill_display_by_admin(admin_client, make_orders, settings):
    settings.LANGUAGE_CODE = 'ru'
    order = Order.objects.get(pk=5)
    order.client_services.add(1, 2)
    response = admin_client.get(
        reverse('payment-systems-detail', args=('bill', )) + '?order=5')
    assert response.status_code == 200
    html = response.json()['html']
    assert 'Счет №5' in html
    assert 'Две тысячи пятьсот рублей, пятьдесят копеек' in html
    assert 'Тестовая категория 1' in html
    assert '14001,83' in html
    assert '25' in html


def test_sberbank_rest_display_by_admin(admin_client, make_orders, mocker):
    SberbankRest._create_order = mocker.MagicMock(return_value='redirect_url')
    response = admin_client.get(
        reverse('payment-systems-detail', args=('sberbank-rest', )) +
        '?order=5')
    assert response.status_code == 200
    html = response.json()['html']
    assert 'redirect_url' in html


def test_sberbank_rest_display_invalid_by_admin(admin_client, make_orders,
                                                mocker):
    SberbankRest._create_order = mocker.MagicMock(return_value=False)
    response = admin_client.get(
        reverse('payment-systems-detail', args=('sberbank-rest', )) +
        '?order=5')
    assert response.status_code == 200
    html = response.json()['html']
    assert 'Извините! Произошла ошибка при обработке платежа.' in html


def test_sberbank_rest_response(client, make_orders, mailoutbox, mocker):

    SberbankRest._get_order = mocker.MagicMock(return_value={
        'orderStatus': '1',
        'orderNumber': '5_test'
    })
    url = reverse('finances:payment-system-response', args=('sberbank-rest', ))
    response = client.get(url + '')
    assert response.status_code == 400
    assert response.content == b'ID of the order is not received.'

    response = client.get(url + '?orderId=order_id', follow=True)

    assert response.status_code == 200
    assert 'Your payment was successful' in str(response.content)

    order = Order.objects.get(pk=5)
    now = arrow.now().datetime
    format = '%d.%m.%Y %H:%I'
    assert order.status == 'paid'
    assert order.payment_system == 'sberbank-rest'
    assert order.paid_date.strftime(format) == now.strftime(format)

    mail = mailoutbox[-1]
    assert mail.recipients() == [order.client.email]
    assert 'Спасибо за Ваш платеж' in mail.subject


def test_sberbank_display_by_admin(admin_client, make_orders):
    response = admin_client.get(
        reverse('payment-systems-detail', args=('sberbank', )) + '?order=5')
    assert response.status_code == 200
    html = response.json()['html']
    assert "api_token: 'sberbank_api_token'" in html
    assert 'http://sberbank.url' in html
    assert 'order.mb_id = 5;' in html
    assert '2,500.50' in html


def test_sberbank_response(client, make_orders, mailoutbox):
    url = reverse('finances:payment-system-response', args=('sberbank', ))
    response = client.post(url)
    assert response.status_code == 400
    assert response.content == b'Bad request.'

    data = {
        'mb_id': '1212',
        'status': 'invalid_status',
        'amount': 'invalid_amount',
    }

    response = client.post(url, data)
    assert response.status_code == 400
    assert response.content == b'Bad request.'

    data['amount'] = '12.22'

    response = client.post(url, data)
    assert response.status_code == 400
    assert response.content == b'Order #1212 not found.'

    data['mb_id'] = '5'
    response = client.post(url, data)
    assert response.status_code == 400
    assert response.content == b'Invalid price'

    data['amount'] = '250050'
    response = client.post(url, data)
    assert response.status_code == 400
    assert response.content == b'Invalid status'

    data.update({
        'status': 'DEPOSITED',
        'formattedAmount': '1200,00',
        'currency': '643',
        'approvalCode': '123456',
        'orderNumber': '11004',
        'panMasked': '555555XXXXXX5599',
        'refNum': '111111111111',
        'paymentDate': '03.08.2018 15:28:26',
        'formattedFeeAmount': '0,00',
        'digest': 'test'
    })

    response = client.post(url, data)
    assert response.status_code == 400
    assert response.content == b'Invalid signature'

    data['digest'] = '5C587E628BDBD482CFF0F5A6F6E5F549152DBE44C'\
                     '747718CDD0308BAA67A4176'

    response = client.post(url, data)

    assert response.status_code == 200
    assert response.content == b'OK'

    order = Order.objects.get(pk=5)
    now = arrow.now().datetime
    format = '%d.%m.%Y %H:%I'
    assert order.status == 'paid'
    assert order.payment_system == 'sberbank'
    assert order.paid_date.strftime(format) == now.strftime(format)
    assert order.transactions.first().data == data

    mail = mailoutbox[-1]
    assert mail.recipients() == [order.client.email]
    assert 'Спасибо за Ваш платеж' in mail.subject


def test_paypal_display_by_admin(admin_client, make_orders):
    response = admin_client.get(
        reverse('payment-systems-detail', args=('paypal', )) + '?order=4')
    assert response.status_code == 200
    html = response.json()['html']
    assert "production: 'paypal_client_id'" in html
    assert 'result.mb_id = parseInt("4");' in html
    assert '12500.00' in html


def test_manager_get_paypal(make_orders):
    paypal = manager.get('paypal', Order.objects.get(pk=4))
    assert isinstance(paypal, Paypal)
    assert paypal.client_id == 'paypal_client_id'
    assert paypal.secret == 'paypal_secret'


def test_paypal_response(client, make_orders, mailoutbox, mocker):
    class TransactionMock(object):
        def __init__(self, amount):
            self.amount = amount
            self.custom = 4

    class AmountMock(object):
        def __init__(self, total, currency):
            self.total = total
            self.currency = currency

    class PaymentMock(object):
        def __init__(self):
            self.state = 'approved'
            self.transactions = [TransactionMock(AmountMock('12500', 'EUR'))]

    paypalrestsdk.Payment.find = mocker.MagicMock(return_value=PaymentMock())
    url = reverse('finances:payment-system-response', args=('paypal', ))
    response = client.post(url)
    assert response.status_code == 400
    assert response.content == b'Bad request.'

    data = {
        'id': 'payment id',
        'mb_id': '1212',
        'state': 'failed',
        'currency': 'invalid_currency',
    }

    response = client.post(url, data)
    assert response.status_code == 400
    assert response.content == b'Bad request.'

    data['total'] = '12.22'

    response = client.post(url, data)
    assert response.status_code == 400
    assert response.content == b'Order #1212 not found.'

    data['mb_id'] = '4'
    response = client.post(url, data)
    assert response.status_code == 400
    assert response.content == b'Invalid price'

    data['total'] = '12500'
    response = client.post(url, data)
    assert response.status_code == 400
    assert response.content == b'Invalid currency'

    data['currency'] = 'EUR'
    response = client.post(url, data)
    assert response.status_code == 400
    assert response.content == b'Invalid status'

    data['state'] = 'approved'
    response = client.post(url, data)
    assert response.status_code == 200
    assert response.content == b'OK'

    order = Order.objects.get(pk=4)
    now = arrow.now().datetime
    format = '%d.%m.%Y %H:%I'
    assert order.status == 'paid'
    assert order.payment_system == 'paypal'
    assert order.paid_date.strftime(format) == now.strftime(format)
    assert order.transactions.first().data == data

    mail = mailoutbox[-1]
    assert mail.recipients() == [order.client.email]
    assert 'Thank you for your payment!' in mail.subject


def test_paypal_response_webhook(client, make_orders):
    """
    Should be able to process webhooks from the Paypal
    """
    url = reverse('finances:payment-system-response', args=('paypal', ))
    response = client.post(url)
    assert response.status_code == 400
    assert response.content == b'Bad request.'

    data = json.dumps({
        "id": "WH-8VE479231F4043730-0PU210753V239925U",
        "event_version": "1.0",
        "create_time": "2019-05-22T09:28:52.275Z",
        "resource_type": "sale",
        "event_type": "PAYMENT.SALE.COMPLETED",
        "summary": "Payment completed for $ 1.0 USD",
        "resource": {
            "id": "4FJ15301WT637284K",
            "state": "completed",
            "amount": {
                "total": "12500.00",
                "currency": "EUR",
                "details": {
                    "subtotal": "1.00"
                }
            },
            "payment_mode": "INSTANT_TRANSFER",
            "protection_eligibility": "ELIGIBLE",
            "protection_eligibility_type":
            "ITEM_NOT_RECEIVED_ELIGIBLE,UNAUTHORIZED_PAYMENT_ELIGIBLE",
            "transaction_fee": {
                "value": "0.33",
                "currency": "USD"
            },
            "invoice_number": "4",
            "custom": "4",
            "receipt_id": "1206484636933976",
            "parent_payment": "PAYID-LTSRKZY6C451945F7163081L",
            "create_time": "2019-05-22T09:28:47Z",
            "update_time": "2019-05-22T09:28:47Z",
            "soft_descriptor": "PAYPAL *TEST"
        },
    })
    response = client.post(url, data=data, content_type="application/json")
    assert response.status_code == 200
    assert response.content == b'OK'

    order = Order.objects.get(pk=4)
    assert order.status == 'paid'
