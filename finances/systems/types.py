from abc import ABC, abstractproperty

from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _

from ..models import Order


class BaseType(ABC):
    """
    Base payment system
    """

    def __init__(self, order=None):
        self.order = order
        if self.order and not isinstance(self.order, Order):
            self.order = Order.objects.get_for_payment_system(order)

    @abstractproperty
    def id(self):
        """
        Payment type ID
        """
        pass

    @abstractproperty
    def name(self):
        """
        Payment type name
        """
        pass

    @abstractproperty
    def description(self):
        """
        Payment type description
        """
        pass

    @abstractproperty
    def countries(self):
        """
        Payment type countries
        """
        pass

    @abstractproperty
    def countries_excluded(self):
        """
        Payment type excluded countries
        """
        pass

    @abstractproperty
    def html(self):
        """
        Payment type html
        """
        pass


class Bill(BaseType):
    """
    Bill payment system
    """
    id = 'bill'
    name = _('bill')
    description = _('bill description')
    template = 'finances/bill.html'
    countries_excluded = []
    countries = ['ru']

    @property
    def html(self):
        return render_to_string(self.template, {'order': self.order})


class Rbk(BaseType):
    """
    Rbk payment system
    """
    id = 'rbk'
    name = _('rbk')
    description = _('rbk description')
    html = ''
    countries_excluded = []
    countries = ['ru']


class Stripe(BaseType):
    """
    Stripe payment system
    """
    id = 'stripe'
    name = _('stripe')
    description = _('stripe description')
    html = ''
    countries_excluded = ['ru']
    countries = []
