import pytest
from django.conf import settings
from django.core.urlresolvers import reverse

from billing.lib.test import json_contains

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
