import pytest
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


def test_payment_system_display_by_admin(admin_client, make_orders):
    response = admin_client.get(
        reverse('payment-systems-detail', args=('stripe', )) + '?order=1')
    assert response.status_code == 200
    response_json = response.json()
    assert 'html' in response_json
    response_json['id'] = 'stripe'
