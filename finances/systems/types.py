import logging
from abc import ABC, abstractmethod
from hashlib import sha512

import stripe
from django.conf import settings
from django.http import (HttpResponse, HttpResponseBadRequest,
                         HttpResponseRedirect)
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
from num2words import num2words

from ..models import Order, Transaction


class BaseType(ABC):
    """
    Base payment system
    """
    invalid_template = 'finances/invalid_type.html'

    def __init__(self, order=None, request=None):
        self.order = order
        self.request = request
        self.payer = self.order.get_payer(
            self.client_filter_fields) if self.order else None
        if self.order and not isinstance(self.order, Order):
            self.order = Order.objects.get_for_payment_system(order)

    @property
    @abstractmethod
    def id(self):
        """
        Payment type ID
        """
        pass

    @property
    @abstractmethod
    def name(self):
        """
        Payment type name
        """
        pass

    @property
    @abstractmethod
    def client_filter_fields(self):
        """
        Client payer not null fields
        """
        pass

    @abstractmethod
    def description(self):
        """
        Payment type description
        """
        pass

    @property
    @abstractmethod
    def countries(self):
        """
        Payment type countries
        """
        pass

    @property
    @abstractmethod
    def template(self):
        """
        Payment type template
        """
        pass

    @property
    @abstractmethod
    def countries_excluded(self):
        """
        Payment type excluded countries
        """
        pass

    @property
    @abstractmethod
    def currencies(self):
        """
        Payment type currencies
        """
        pass

    @property
    @abstractmethod
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
        if not self.order or not self.payer:
            return self.invalid_template
        if self.order.price.currency.code not in self.currencies:
            return self.invalid_template
        if self.order.client.status not in ('active', 'disabled'):
            return self.invalid_template
        return self.template

    @property
    def service_name(self):
        if not self.order:
            return None
        return _('order') + ' #' + str(self.order.pk)

    @property
    def client(self):
        return getattr(self.order, 'client', None)

    def _process_order(self, data):
        self.order.set_paid(self.id)

        transaction = Transaction()
        transaction.set_data(data)
        transaction.order = self.order
        transaction.save()


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
    currencies = ['RUB']
    client_filter_fields = ('phone', 'address', 'postal_code', 'region',
                            'city')

    @property
    def html(self):
        data = {}
        if self.order:
            price_text = num2words(
                self.order.price.amount,
                lang='ru',
                to='currency',
                currency='RUB')
            data = {
                'order': self.order,
                'payer': self.payer,
                'request': self.request,
                'recipient': settings.MB_BILL_RECIPIENT_COMPANY,
                'price_text': price_text
            }

        return render_to_string(self.get_template, data)


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
    currencies = ['RUB', 'EUR']
    client_filter_fields = ('phone', )

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
            '',
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
        if recipient_currency != self.currency:
            return HttpResponseBadRequest('Invalid currency.')
        if str(self.order.price.amount) != recipient_amount:
            return HttpResponseBadRequest('Invalid payment amount.')

        self._process_order(request.POST)

        return HttpResponse('OK')

    @property
    def currency(self):
        if not self.order:
            return None
        code = self.order.price.currency.code
        return 'RUR' if code == 'RUB' else code

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
    countries_excluded = ['ru']
    countries = []
    currencies = ['EUR']
    client_filter_fields = ('phone', )

    # Stripe config
    publishable_key = settings.STRIPE_PUBLISHABLE_KEY
    secret_key = settings.STRIPE_SECRET_KEY

    @property
    def price_in_cents(self):
        if not self.order:
            return None
        return int(self.order.price.amount * 100)

    def response(self, request):
        """
        Check payment system calback response
        """
        order_id = request.POST.get('order_id')
        token = request.POST.get('stripeToken')
        email = request.POST.get('stripeEmail')
        logger = logging.getLogger('billing')

        if not all([order_id, token, email]):
            return HttpResponseBadRequest('Bad request.')

        self.order = Order.objects.get_for_payment_system(order_id)
        if not self.order:
            return HttpResponseBadRequest(
                'Order #{} not found.'.format(order_id))
        client = self.order.client
        if client.email != email:
            return HttpResponseBadRequest('Invalid client email.')

        stripe.api_key = self.secret_key
        try:
            charge = stripe.Charge.create(
                source=token,
                amount=self.price_in_cents,
                currency='eur',
                description=self.service_name)

            logger.info('Stripe response {}'.format(charge))
        except stripe.error.StripeError as error:
            logger.info('Stripe error {}'.format(error))
            return HttpResponseBadRequest(
                'Stripe error. Your card was declined')

        self._process_order(charge)

        return HttpResponseRedirect(client.url
                                    if client.url else settings.MB_SITE_URL)

    @property
    def html(self):
        return render_to_string(self.get_template, {
            'order': self.order,
            'request': self.request,
            'stripe': self
        })
