"""
The exchange rates tests
"""
from decimal import Decimal

import pytest
from django.urls import reverse
from djmoney.money import Money

from billing.lib.test import json_contains
from finances.lib import rates

pytestmark = pytest.mark.django_db

MSG_CURRENCIES = 'Current exchange rates: AED: 4.153797; AFN: 85.160322;'


def _get_first_log_messages(caplog) -> list:
    return [r.msg for r in caplog.records]


def _get_money_sample() -> Money:
    return Money(1.5, 'EUR')


def test_rates_list_by_user(client):
    """
    The endpoint should not be available to unauthenticated users
    """
    response = client.get(reverse('rate-list'))
    assert response.status_code == 401


def test_rates_list_by_admin(admin_client):
    """
    The endpoint should return a list of the rates
    """
    response = admin_client.get(reverse('rate-list'))

    assert response.status_code == 200
    assert len(response.json()) == 168
    json_contains(response, 'EUR')
    json_contains(response, 'USD')
    json_contains(response, '$')
    json_contains(response, '€')


def test_log_exchange_rates(caplog):
    rates.log_exchange_rates()
    msg = _get_first_log_messages(caplog)
    assert MSG_CURRENCIES in msg[0]


def test_update_exchange_rates(caplog, mocker):
    rates.call_command = mocker.MagicMock(return_value=True)
    rates.update_exchange_rates()
    msg = _get_first_log_messages(caplog)
    assert MSG_CURRENCIES in msg[0]
    assert 'Rates have been updated.' in msg[1]


def test_get_exchange_rates():
    assert rates.get_exchange_rate(
        'RUB', 'EUR') == Decimal('0.01348868485484529476634171705')

    assert rates.get_exchange_rate('EUR', 'RUB') == Decimal('74.136212')
    assert rates.get_exchange_rate('EUR', 'USD') == Decimal('1.130902')
    assert rates.get_exchange_rate('EUR', 'EUR') == Decimal(1)
    assert rates.get_exchange_rate(
        'RUB', 'KZT') == Decimal('5.723602036748249290104004774')


def test_get_exchange_rates_invalid_currency():
    assert rates.get_exchange_rate('EUR', 'XXX') is None
    assert rates.get_exchange_rate('NNN', 'USD') is None


def test_convert_money():
    money = _get_money_sample()
    assert rates.convert_money(money, 'RUB') == Money('111.2043180', 'RUB')
    assert rates.convert_money(money, 'EUR') == money
    assert rates.convert_money(money, 'KZT') == Money('636.4892610', 'KZT')


def test_convert_money_invalid_curreny():
    money = _get_money_sample()
    assert rates.convert_money(money, 'XXX') is None
