import logging

import braintree

from billing.lib.conf import get_settings


class BraintreeGateway(object):
    """
    The braintree service
    """
    codes = [
        braintree.Transaction.Status.Authorized,
        braintree.Transaction.Status.Authorizing,
        braintree.Transaction.Status.Settled,
        braintree.Transaction.Status.SettlementConfirmed,
        braintree.Transaction.Status.SettlementPending,
        braintree.Transaction.Status.Settling,
        braintree.Transaction.Status.SubmittedForSettlement
    ]

    def __init__(self, country, environment='prod'):
        self.country = country
        self.logger = logging.getLogger('billing')
        self.merchant_id = get_settings(
            'BRAINTREE_MERCHANT_ID', country=self.country)
        self.public_key = get_settings(
            'BRAINTREE_PUBLIC_KEY', country=self.country)
        self.private_key = get_settings(
            'BRAINTREE_PRIVATE_KEY', country=self.country)
        if environment == 'prod':
            env = braintree.Environment.Production
        else:
            env = braintree.Environment.Sandbox

        self.gateway = braintree.BraintreeGateway(
            braintree.Configuration(
                environment=env,
                merchant_id=self.merchant_id,
                public_key=self.public_key,
                private_key=self.private_key,
            ))

    def sale(self, token, amount):
        """
        Make the transaction
        """
        result = self.gateway.transaction.sale({
            'amount': amount,
            'payment_method_nonce': token,
            'options': {
                "submit_for_settlement": True
            }
        })
        self.logger.info('Braintree sale response {}'.format(result))
        tr = result.transaction
        if result.is_success and self.check_transaction(tr):
            return tr
        else:
            return False

    def check_transaction(self, tr):
        """
        Check the transaction status code
        """
        return tr and tr.status in self.codes

    def token(self):
        """
        Generate the client token
        """
        try:
            return self.gateway.client_token.generate()
        except braintree.exceptions.braintree_error.BraintreeError:
            return 'invalid_braintree_token'

    def create_customer(self, token, client):
        """
        Create the customer for the client
        """
        result = self.gateway.customer.create({
            'first_name':
            client.first_name,
            'last_name':
            client.last_name,
            'email':
            client.email,
            'phone':
            str(client.phone) if client.phone else None,
            'website':
            client.url,
            'payment_method_nonce':
            token
        })
        self.logger.info('Braintree customer response {}'.format(result))

        c = result.customer
        if not result.is_success or not c or not c.payment_methods:
            return None
        return c

    def create_subscription(self, token, period, price):
        """
        Create the subscription for the client
        """
        result = self.gateway.subscription.create({
            'payment_method_token':
            token,
            'plan_id':
            period,
            'price':
            price,
            'options': {
                'start_immediately': True
            }
        })

        self.logger.info('Braintree subscription response {}'.format(result))
        subscription = result.subscription
        if not result.is_success or not subscription:
            return None
        return subscription

    def cancel_subscription(self, id):
        try:
            result = self.gateway.subscription.cancel(id)
            self.logger.info(
                'Braintree cancel subscription response {}'.format(result))
        except braintree.exceptions.NotFoundError:
            return True
        return result

    def get_subscription(self, id):
        try:
            result = self.gateway.subscription.find(id)
        except braintree.exceptions.NotFoundError:
            return {'error': 'The subscription not found.'}
        return result
