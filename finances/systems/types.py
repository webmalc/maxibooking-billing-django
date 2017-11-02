from abc import ABC, abstractproperty
from hashlib import sha512

from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest
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
    def url(self):
        return self.order.client.url if self.order else None

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

    def _calc_signature(self, data):
        return sha512('::'.join(map(str, data)).encode('utf-8')).hexdigest()

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
        return self._calc_signature(data)

    def response(self, request):
        """
        Check payment system calback response
        """
        order_id = request.POST.get('orderId')
        eshop_id = request.POST.get('eshopId')
        service_name = request.POST.get('serviceName')
        eshop_account = request.POST.get('eshopAccount')
        recipient_amount = request.POST.get('recipientAmount')
        recipient_currency = request.POST.get('recipientCurrency')
        payment_status = request.POST.get('paymentStatus')
        username = request.POST.get('userName')
        email = request.POST.get('userEmail')
        payment_date = request.POST.get('paymentData')
        request_hash = request.POST.get('hash')

        if not all([eshop_id, payment_status, request_hash, payment_status]):
            return HttpResponseBadRequest('Bad request.')
        if int(payment_status) != 5:
            return HttpResponseBadRequest('Invalid payment status != 5.')

        self.order = Order.objects.get_for_payment_system(order_id)
        if not self.order:
            return HttpResponseBadRequest(
                'Order #{} not found.'.format(order_id))

        signature = self._calc_signature([
            eshop_id, order_id, service_name, eshop_account, recipient_amount,
            recipient_currency, payment_status, username, email, payment_date,
            self.secret_key
        ])
        if request_hash != signature:
            return HttpResponseBadRequest('Invalid signature.')
        if request_hash != signature:
            return HttpResponseBadRequest('Invalid signature.')
        if recipient_currency != self.currency:
            return HttpResponseBadRequest('Invalid currency.')
        if str(self.order.price.amount) != recipient_amount:
            return HttpResponseBadRequest('Invalid payment amount.')

        self.order.set_paid('rbk')

        return HttpResponse('OK')

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
