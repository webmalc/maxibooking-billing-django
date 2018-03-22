import logging

from django.apps import apps

from billing.lib.utils import clsfstr
from hotels.models import Country


class Exception(Exception):
    pass


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
        if country and not isinstance(country, Country):
            country = Country.objects.get(pk=country)
        if not country:
            country = getattr(self, 'country', None)
        if not quantity or not country:
            raise Exception('Invalid country - {} or quantity - {}'.format(
                country, quantity))

        prices = list(
            apps.get_model('finances.Price').objects.filter_by_country(
                country, self.service))
        if not prices:
            raise Exception('Empty prices.')

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

        template = """
'Calc result: {}. Prices: {}. Country: {}. \
Quantity: {}. Service: {}. Table: {}'.
        """
        logging.getLogger('billing').info(
            template.format(
                total,
                prices,
                country,
                quantity,
                self.service,
                table,
            ))

        return total


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
