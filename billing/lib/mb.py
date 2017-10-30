import json
import logging
import time

from django.conf import settings
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

import requests

from .messengers.mailer import mail_client


def _request(url, data, error_callback):
    """
    Send request to maxibooking
    """
    for i in range(0, 10):
        try:
            response = requests.post(
                url, timeout=settings.MB_TIMEOUT, json=data)
            if response.status_code == 200:
                content = response.content
                try:
                    return json.loads(content)
                except json.decoder.JSONDecodeError:
                    return response
        except requests.exceptions.RequestException:
            pass

        if not getattr(settings, 'TESTS', False):
            time.sleep(settings.MB_TIMEOUT)

    else:
        error_callback()

    return False


def mb_settings(client=None, country=None):
    """
    Get MB_URLS by country code
    """
    if not client and not country:
        raise AttributeError('client is None and country is None.')
    if not country and client:
        country = client.country.tld
    return settings.MB_URLS.get(country, settings.MB_URLS['__all__'])


def client_fixtures(client):
    """
    Install client fixtures
    """
    logging.getLogger('billing').info(
        'Begin client fixtures installation. Id: {}; login: {}'.format(
            client.id, client.login))

    urls = mb_settings(client)

    def _error_callback():
        logging.getLogger('billing').error(
            'Failed client fixtures installation. Id: {}; login: {}'.format(
                client.id, client.login))
        mail_client(
            subject=_('Registation failed'),
            template='emails/registration_fail.html',
            data={},
            client=client)

    return _request(
        url=urls['fixtures'],
        data={
            'client_login': client.login,
            'token': urls['token'],
            'results_url': reverse(
                'client-install-result', args=[client.login])
        },
        error_callback=_error_callback)


def client_install(client):
    """
    Client installation
    """
    logging.getLogger('billing').info(
        'Begin client installation. Id: {}; login: {}'.format(
            client.id, client.login))

    urls = mb_settings(client)

    def _error_callback():
        logging.getLogger('billing').error(
            'Failed client installation. Id: {}; login: {}'.format(
                client.id, client.login))
        mail_client(
            subject=_('Registation failed'),
            template='emails/registration_fail.html',
            data={},
            client=client)

    return _request(
        url=urls['install'],
        data={
            'client_login': client.login,
            'token': urls['token'],
            'results_url': reverse(
                'client-install-result', args=[client.login])
        },
        error_callback=_error_callback)


def client_archive(client):
    """
    Client archivation
    """
    logging.getLogger('billing').info(
        'Begin client archivation. Id: {}; login: {}'.format(
            client.id, client.login))

    urls = mb_settings(client)

    def _error_callback():
        logging.getLogger('billing').error(
            'Failed client archivation. Id: {}; login: {}'.format(
                client.id, client.login))

    result = _request(
        url=urls['archive'],
        data={'client_login': client.login,
              'token': urls['token']},
        error_callback=_error_callback)
    if result:
        client.status = 'archived'
        client.save()

    return result
