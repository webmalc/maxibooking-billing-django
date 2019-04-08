import logging
from typing import Optional

import moneyed
from django.apps import apps

from billing.lib.utils import clsfstr

from .rates import convert_money

CURRENCIES_CODES = moneyed.CURRENCIES.keys()


def get_currency_by_country(country) -> Optional[moneyed.Currency]:
    country = get_country_by_tld_or_name(country)
    names = [country.name_en.upper()]
    names += [x.upper() for x in country.alternate_names.split(',')]

    for code, currency in moneyed.CURRENCIES.items():
        for name in names:
            if name in currency.countries:
                return currency
    return None


def get_country_by_tld_or_name(country):
    country_model = apps.get_model('hotels.Country')
    try:
        if country and str(country).isnumeric() and not isinstance(
                country, country_model):
            country = country_model.objects.get(pk=country)
        elif country and not str(country).isnumeric() and not isinstance(
                country, country_model):
            country = country_model.objects.filter(tld=country).first()
    except country_model.DoesNotExist:
        country = None

    return country


class CalcException(Exception):
    pass


class CalcByQantityPeriodCountry(object):
    """
    Calculate the service price by the period, country and quantity
    """

    def __init__(self, period: int, period_units: str, quantity: int,
                 country: str) -> None:
        self.period = period
        self.period_units = period_units
        self.quantity = quantity
        self.country = get_country_by_tld_or_name(country)
        self.services = []  # type: list

    def get_prices(self):
        self._fill_services_for_calcualtion()
        prices = self._calc_services()

        if not len(prices):
            raise CalcException('Prices are empty')

        return prices

    def _fill_services_for_calcualtion(self):
        service_model = apps.get_model('finances.Service')
        if self.period:
            service = service_model.objects.get_by_period(
                service_type='rooms',
                period=self.period,
                period_units=self.period_units,
            )
            if not service:
                raise CalcException('Service not found.')
            self.services.append(service)
        else:
            self.services = service_model.objects.get_all_periods(
                service_type='rooms',
                period_units=self.period_units,
            )

    def _get_local_price(self, price: moneyed.Money) -> moneyed.Money:
        """
        Get the local price according to the country currency
        """
        currency = getattr(self.country, 'currency')
        if currency and currency != price.currency:
            return convert_money(price, currency)
        return price

    def _calc_services(self) -> list:
        prices = []
        for service in self.services:
            price = Calc.factory(service).calc(
                quantity=self.quantity, country=self.country)
            price_local = self._get_local_price(price)
            prices.append({
                'status':
                True,
                'price':
                price.amount,
                'price_currency':
                price.currency.code,
                'period':
                service.period,
                'price_local':
                price_local.amount if price_local else None,
                'price_currency_local':
                price_local.currency.code if price_local else None
            })

        return prices


class CalcByQuery(CalcByQantityPeriodCountry):
    """
    Calculate the service price by the query serializer
    """

    def __init__(self, query: dict) -> None:
        super().__init__(
            query.get('period'),
            query.get('period_units'),
            query.get('quantity'),
            query.get('country'),
        )


class Calc(object):
    """
    Calc abstract class
    """

    def __init__(self, entry):
        if isinstance(entry, apps.get_model('clients.ClientService')):
            self.client_service = entry
            self.quantity = entry.quantity
            self.country = entry.client.country
        self.service = self._get_service(entry)

    @staticmethod
    def _get_service(entry):
        """
        Get service object by id
        """
        if isinstance(entry, apps.get_model('clients.ClientService')):
            service = entry.service
        elif isinstance(entry, apps.get_model('finances.Service')):
            service = entry
        else:
            service = apps.get_model('finances.Service').objects.get(pk=entry)
        return service

    @staticmethod
    def factory(entry, country=None):
        """
        Factory method (entry - Service or ClientService or int)
        """
        service = Calc._get_service(entry)
        class_name = service.type.title().replace('_', '')

        return clsfstr('finances.lib.calc', class_name)(entry)

    def calc(self, quantity=None, country=None):
        """
        Calc price
        """
        if not quantity:
            quantity = getattr(self, 'quantity', None)

        country = self._get_country(country)

        if not quantity or not country:
            raise CalcException('Invalid country or quantity.')

        prices = list(
            apps.get_model('finances.Price').objects.filter_by_country(
                country, self.service))
        if not prices:
            raise CalcException('Empty prices.')

        total = self._do_calc_total_price(prices, quantity)
        self._log_calc_result(total, prices, country, quantity)

        return total

    def _get_country(self, country):
        """
        Polymorph getting of country
        """
        country = get_country_by_tld_or_name(country)
        if not country:
            country = getattr(self, 'country', None)

        return country

    def _do_calc_total_price(self, prices, quantity):
        """
        Calculate price based on prices table and quantity
        """
        table = []
        default = [d for d in prices if d.for_unit]

        for r in range(1, quantity + 1):
            p = [
                p for p in prices
                if (p.period_from is None or p.period_from <= r) and (
                    p.period_to is None or p.period_to >= r)
            ]
            if p and not p[0].for_unit and p[0] in table:
                p[0] = 0
            if not p:
                p.append(default[0] if default else 0)
            table.append(p[0])

        total = 0
        for item in table:
            total += getattr(item, 'price', 0)
        return total

    def _log_calc_result(self, total, prices, country, quantity):
        """
        Log the result of calculation
        """
        template = """
'Calc result: {}. Prices: {}. Country: {}. \
Quantity: {}. Service: {}.'
        """
        logging.getLogger('billing').info(
            template.format(
                total,
                prices,
                country,
                quantity,
                self.service,
            ))


class Rooms(Calc):
    """
    Calc rooms service
    """
    pass


class Other(Calc):
    """
    Calc other service
    """
    pass
