import hashlib
import hmac
import logging
from abc import ABC, abstractmethod
from hashlib import sha512

import paypalrestsdk
import stripe
from django.conf import settings
from django.core.exceptions import ValidationError
from django.http import (HttpResponse, HttpResponseBadRequest,
                         HttpResponseRedirect)
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
from num2words import num2words
from weasyprint import HTML

from billing.lib.conf import get_settings

from ..models import Order, Subscription, Transaction
from .lib import BraintreeGateway


class TypeException(Exception):
    """
    Type exception
    """
    pass


class BaseType(ABC):
    """
    Base payment system
    """
    invalid_template = 'finances/invalid_type.html'

    def __init__(self, order=None, request=None, load=True):
        self.request = request
        self.order = order
        if self.order and not isinstance(self.order, Order):
            self.order = Order.objects.get_for_payment_system(order)

        if load:
            self.load()

    def load(self):
        self.payer = self.order.get_payer(
            self.client_filter_fields,
            local=self.payer_local_required) if self.order else None
        self.country = self.payer.country if self.payer else None
        self._conf(self.order, self.request)

    @property
    def price_as_str(self):
        """
        The order price
        """
        if not self.order:
            raise ValueError('The order have not set.')
        return str(self.order.price.amount)

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
    def payer_local_required(self):
        """
        Is a local payer required for payment system?
        """
        return True

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
        if not self.order or not self.payer or not self.country:
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

    def _get_url(self, order, path):
        client_url = self.order.client.url
        if not client_url:
            return settings.MB_SITE_URL
        return '{}{}'.format(client_url, path)

    def _get_success_url(self, order):
        return self._get_url(order, '/management/online/api/payment/success')

    def _get_fail_url(self, order):
        return self._get_url(order, '/management/online/api/payment/fail')

    def _conf(self, order=None, request=None):
        """
        Load the config
        """
        pass


class Bill(BaseType):
    """
    Bill payment system
    """
    id = 'bill'
    name = _('bill')
    description = _('Create a bill for non-cash transfer through the Bank')
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

        data['required_fields'] = self.client_filter_fields
        return render_to_string(self.get_template, data)

    @property
    def pdf(self):
        return HTML(string=self.html).write_pdf()


class Sberbank(BaseType):
    """
    Sberbank payment system
    """
    id = 'sberbank'
    name = _('sberbank')
    description = _('Payment by card through the "Sberbank" system')
    template = 'finances/sberbank.html'
    html = ''
    countries_excluded = []
    countries = ['ru']
    currencies = ['RUB']
    client_filter_fields = ('phone', )
    payer_local_required = False

    def _conf(self, order=None, request=None):
        """
        Load config
        """
        self.api_token = settings.SBERBANK_API_TOKEN
        self.secret_key = settings.SBERBANK_SECRET_KEY
        self.js_url = settings.SBERBANK_URL

    def check_signature(self, request):
        vals = [
            request.POST.get('status'),
            request.POST.get('formattedAmount'),
            request.POST.get('currency'),
            request.POST.get('approvalCode'),
            request.POST.get('orderNumber'),
            request.POST.get('panMasked'),
            request.POST.get('refNum'),
            request.POST.get('paymentDate'),
            request.POST.get('formattedFeeAmount'),
            self.secret_key,
            ';',
        ]
        digest = request.POST.get('digest')
        sig_str = ''.join(vals)
        sig = hmac.new(
            str.encode(self.secret_key),
            str.encode(sig_str),
            hashlib.sha256,
        )

        return sig.hexdigest().upper() == digest

    def response(self, request):
        """
        Check payment system calback response
        """
        order_id = request.POST.get('mb_id')
        status = request.POST.get('status')
        amount = request.POST.get('amount')

        if not all([order_id, amount, status]):
            return HttpResponseBadRequest('Bad request.')

        try:
            amount = float(amount) / 100
        except ValueError:
            return HttpResponseBadRequest('Bad request.')

        self.order = Order.objects.get_for_payment_system(order_id)

        if not self.order:
            return HttpResponseBadRequest(
                'Order #{} not found.'.format(order_id))

        if float(self.order.price.amount) != amount:
            return HttpResponseBadRequest('Invalid price')

        if status != 'DEPOSITED':
            return HttpResponseBadRequest('Invalid status')

        if not self.check_signature(request):
            return HttpResponseBadRequest('Invalid signature')

        self._process_order(request.POST)

        return HttpResponse('OK')

    @property
    def html(self):
        return render_to_string(
            self.get_template, {
                'order': self.order,
                'request': self.request,
                'sberbank': self,
                'required_fields': self.client_filter_fields
            })


class Rbk(BaseType):
    """
    Rbk payment system
    """
    id = 'rbk'
    name = _('rbk')
    description = _('Payment by card through the "RBK Money" system')
    template = 'finances/rbk.html'
    html = ''
    countries_excluded = []
    countries = ['ru']
    currencies = ['RUB', 'EUR']
    client_filter_fields = ('phone', )
    payer_local_required = False

    # Rbk config
    action = 'https://rbkmoney.ru/acceptpurchase.aspx'

    def _conf(self, order=None, request=None):
        """
        Load config
        """
        self.shop_id = settings.RBK_SHOP_ID
        self.secret_key = settings.RBK_SECRET_KEY

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
        return render_to_string(
            self.get_template, {
                'order': self.order,
                'rbk': self,
                'required_fields': self.client_filter_fields
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

    def _conf(self, order=None, request=None):
        """
        Load config
        """
        self.publishable_key = get_settings(
            'STRIPE_PUBLISHABLE_KEY', country=self.country)
        self.secret_key = get_settings(
            'STRIPE_SECRET_KEY', country=self.country)

    @property
    def price_in_cents(self):
        if not self.order:
            return None
        return int(self.order.price.amount * 100)

    def _process_request(self, request):
        order_id = request.POST.get('order_id')
        token = request.POST.get('stripeToken')
        email = request.POST.get('stripeEmail')

        if not all([order_id, token, email]):
            raise TypeException('Bad request.')

        self.order = Order.objects.get_for_payment_system(order_id)
        if not self.order:
            raise TypeException('Order #{} not found.'.format(order_id))

        if self.order.client.email != email:
            raise TypeException('Invalid client email.')

        self._conf(order=self.order)

        return token

    def response(self, request):
        """
        Check payment system calback response
        """
        logger = logging.getLogger('billing')
        try:
            token = self._process_request(request)
        except TypeException as e:
            return HttpResponseBadRequest(e)

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

        url = self.order.client.url or settings.MB_SITE_URL
        return HttpResponseRedirect(url)

    @property
    def html(self):
        return render_to_string(self.get_template, {
            'order': self.order,
            'request': self.request,
            'stripe': self
        })


class BraintreeSubscription(BaseType):
    """
    Braintree-subscription payment system
    """
    id = 'braintree-subscription'
    name = _('braintree-subscription')
    description = _('braintree subscription description')
    template = 'finances/braintree.html'
    countries_excluded = ['ru']
    countries = []
    currencies = ['EUR', 'CAD', 'USD']
    client_filter_fields = ('phone', )

    def _conf(self, order=None, request=None):
        """
        Load config
        """
        self.braintree = BraintreeGateway(self.country, 'sandbox')

    def _process_request(self, request):
        order_id = request.POST.get('order_id')
        token = request.POST.get('payment_method_nonce')

        if not all([order_id, token]):
            raise TypeException('Bad request.')

        self.order = Order.objects.get_for_payment_system(order_id)
        self.load()
        if not self.order:
            raise TypeException('Order #{} not found.'.format(order_id))

        return token

    def _create_customer(self, token):
        """ Create a braintree customer if the client does not have one """
        custormer = self.braintree.create_customer(token, self.order.client)
        if not custormer:
            raise TypeException(
                'An error occurred during creation the customer')
        return custormer

    def _create_subscription(self, token):
        """ Create a braintree subscription """
        service = self.order.get_room_service
        if not service:
            raise TypeException(
                'The order does not have a room service object.')

        subscription = self.braintree.create_subscription(
            token,
            service.period_in_months,
            self.order.price.amount,
        )
        if not subscription:
            raise TypeException(
                'An error occurred during creation the subscription')

        # Create the Subscription object
        sub_model = Subscription()
        sub_model.client = self.client
        sub_model.order = self.order
        sub_model.country = self.country
        sub_model.status = 'enabled'
        sub_model.price = self.order.price
        sub_model.period = service.period_in_months
        sub_model.merchant = self.braintree.merchant_id
        sub_model.customer = self.customer.id
        sub_model.subscription = subscription.id
        sub_model.save()
        try:
            sub_model.full_clean()
            sub_model.save()
        except ValidationError:
            self.logger.error(
                'Unable to save the subscription model: {}'.format(
                    subscription))

        return subscription

    def subscription(self, request):
        # TODO: process webhooks
        return HttpResponse('OK')

    def response(self, request):
        """
        Check the payment system calback response
        """
        try:
            token = self._process_request(request)
            self.customer = self._create_customer(token)
            payment_token = self.customer.payment_methods[0].token
            sub = self._create_subscription(payment_token)

        except TypeException as e:
            return HttpResponseBadRequest(e)

        tr = sub.transactions[-1] if sub.transactions else None
        if self.braintree.check_transaction(tr):
            self._process_order(tr)
            return HttpResponseRedirect(self._get_success_url(self.order))
        else:
            return HttpResponseRedirect(self._get_fail_url(self.order))

    @property
    def html(self):
        if Subscription.objects.get_active(self.client).count():
            return render_to_string(
                self.invalid_template, {
                    'error': 'The client already have the subscription',
                })

        else:
            return render_to_string(
                self.get_template, {
                    'order': self.order,
                    'client_token': self.braintree.token(),
                    'request': self.request,
                    'braintree': self,
                    'button': 'subscribe',
                    'required_fields': self.client_filter_fields
                })


class Braintree(BaseType):
    """
    Braintree payment system
    """
    id = 'braintree'
    name = _('braintree')
    description = _('braintree description')
    template = 'finances/braintree.html'
    countries_excluded = ['ru']
    countries = []
    currencies = ['EUR', 'CAD', 'USD']
    client_filter_fields = ('phone', )

    def _conf(self, order=None, request=None):
        """
        Load config
        """
        self.braintree = BraintreeGateway(self.country)

    def _process_request(self, request):
        order_id = request.POST.get('order_id')
        token = request.POST.get('payment_method_nonce')

        if not all([order_id, token]):
            raise TypeException('Bad request.')

        self.order = Order.objects.get_for_payment_system(order_id)
        if not self.order:
            raise TypeException('Order #{} not found.'.format(order_id))

        return token

    def response(self, request):
        """
        Check the payment system calback response
        """
        try:
            token = self._process_request(request)
        except TypeException as e:
            return HttpResponseBadRequest(e)
        tr = self.braintree.sale(token, self.order.price.amount)
        if tr:
            self._process_order(tr)
            return HttpResponseRedirect(self._get_success_url(self.order))
        else:
            return HttpResponseRedirect(self._get_fail_url(self.order))

    @property
    def html(self):
        return render_to_string(
            self.get_template, {
                'order': self.order,
                'client_token': self.braintree.token(),
                'request': self.request,
                'braintree': self,
                'button': 'pay',
                'required_fields': self.client_filter_fields
            })


class Paypal(BaseType):
    """
    Paypal payment system
    """
    id = 'paypal'
    name = _('paypal')
    description = _('paypal description')
    template = 'finances/paypal.html'
    countries_excluded = []
    countries = ['us', 'ca']
    currencies = ['CAD', 'USD', 'EUR']
    client_filter_fields = ('phone', )

    def _conf(self, order=None, request=None):
        """
        Load the configuration
        """
        self.client_id = get_settings('PAYPAL_CLIENT_ID', country=self.country)
        self.secret = get_settings('PAYPAL_SECRET', country=self.country)

        paypalrestsdk.configure({
            'mode': 'sandbox',  # sandbox or live
            'client_id': self.client_id,
            'client_secret': self.secret
        })

    def response(self, request):
        """
        Check the payment system calback response
        """

        order_id = request.POST.get('mb_id')
        status = request.POST.get('state')
        amount = request.POST.get('total')
        currency = request.POST.get('currency')
        id = request.POST.get('id')

        if not all([order_id, amount, status, currency, id]):
            return HttpResponseBadRequest('Bad request.')

        self.order = Order.objects.get_for_payment_system(order_id)

        if not self.order:
            return HttpResponseBadRequest(
                'Order #{} not found.'.format(order_id))

        if float(self.order.price.amount) != float(amount):
            return HttpResponseBadRequest('Invalid price')

        if self.order.price.currency.code != currency:
            return HttpResponseBadRequest('Invalid currency')

        if status == 'failed':
            return HttpResponseBadRequest('Invalid status')

        try:
            payment = paypalrestsdk.Payment.find(id)
            transaction = payment.transactions[0]
            payment_amount = transaction.amount
        except paypalrestsdk.exceptions.ResourceNotFound:
            return HttpResponseBadRequest('Invalid payment')

        if int(transaction.custom) != self.order.id:
            return HttpResponseBadRequest('Invalid payment order')

        if payment.state != status:
            return HttpResponseBadRequest('Invalid payment status')

        if float(payment_amount.total) != float(amount):
            return HttpResponseBadRequest('Invalid payment price')

        if payment_amount.currency != currency:
            return HttpResponseBadRequest('Invalid payment currency')

        self._process_order(request.POST)

        return HttpResponse('OK')

    @property
    def html(self):
        return render_to_string(
            self.get_template, {
                'order': self.order,
                'request': self.request,
                'paypal': self,
                'required_fields': self.client_filter_fields
            })
