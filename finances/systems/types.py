from abc import ABC, abstractproperty
from hashlib import sha512

from django.conf import settings
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
    def template(self):
        """
        Payment type template
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

    @property
    def get_template(self):
        return self.template if self.order else 'finances/invalid_type.html'


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
        return render_to_string(self.get_template, {'order': self.order})


class Rbk(BaseType):
    """
    Rbk payment system
    """
    id = 'rbk'
    name = _('rbk')
    description = _('rbk description')
    template = 'finances/rbk.html'
    html = ''
    countries_excluded = []
    countries = ['ru']

    # Rbk config
    action = 'https://rbkmoney.ru/acceptpurchase.aspx'
    shop_id = settings.RBK_SHOP_ID
    secret_key = settings.RBK_SECRET_KEY

    @property
    def signature(self):
        data = (
            self.shop_id,
            str(self.order.price.amount),
            self.currency,
            self.order.client.email,
            self.service_name,
            self.order.pk,
            self.secret_key,
        )
        return sha512('::'.join(map(str, data)).encode('utf-8')).hexdigest()

    @property
    def currency(self):
        if not self.order:
            return None
        code = self.order.price.currency.code
        return 'RUR' if code == 'RUB' else code

    @property
    def service_name(self):
        if not self.order:
            return None
        return _('order') + ' #' + str(self.order.pk)

    @property
    def html(self):
        return render_to_string(self.get_template, {
            'order': self.order,
            'rbk': self
        })


class Stripe(BaseType):
    """
    Stripe payment system
    """
    id = 'stripe'
    name = _('stripe')
    description = _('stripe description')
    template = 'finances/stripe.html'
    html = ''
    countries_excluded = ['ru']
    countries = []
