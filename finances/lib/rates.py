import logging
from decimal import Decimal
from typing import Optional

from django.core.management import call_command
from djmoney.contrib.exchange.exceptions import MissingRate
from djmoney.contrib.exchange.models import Rate
from djmoney.contrib.exchange.models import convert_money as base_convert_money
from djmoney.contrib.exchange.models import get_rate
from djmoney.money import Money

logger = logging.getLogger('billing')


def update_exchange_rates():
    """
    Update the exchange rates from the remote source
    """
    log_exchange_rates()
    call_command('update_rates')
    logger.info('Rates have been updated.')


def log_exchange_rates():
    """
    Log current exchange rates
    """
    rates = Rate.objects.values('currency', 'value').order_by('currency')
    rates_str = '; '.join(['{currency}: {value}'.format(**r) for r in rates])
    logger.info('Current exchange rates: {}'.format(rates_str))


def get_exchange_rate(base_currency: str,
                      target_currency: str) -> Optional[Decimal]:
    """
    Get an exchange rate
    """
    try:

        return get_rate(base_currency, target_currency)
    except MissingRate as e:
        logger.error('Exchange rates error: {}'.format(str(e)))
    return None


def convert_money(money: Money, targer_currency) -> Optional[Money]:
    """
    Convert a money value according to the current exchange rates
    """
    try:
        return base_convert_money(money, targer_currency)
    except MissingRate as e:
        logger.error('Exchange rates error: {}'.format(str(e)))
    return None
