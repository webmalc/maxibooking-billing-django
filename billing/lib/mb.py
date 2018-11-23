import json
import logging
import time

import requests
from django.conf import settings
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from .conf import get_settings
from .messengers.mailer import mail_client


def _request(url, data, error_callback):
    """
    Send request to maxibooking
    """
    for i in range(0, 10):
        try:
            logging.getLogger('billing').info(
                'Mb service begin request: url: {}, data: {}'.format(
                    url, data))
            response = requests.post(
                url, timeout=settings.MB_TIMEOUT, json=data)
            if response.status_code == 200:
                content = response.content
                try:
                    json_response = json.loads(content)

                    logging.getLogger('billing').info(
                        'Mb service json response: {}. url: {}, data: {}'.
                        format(json_response, url, data))
                    return json_response
                except json.decoder.JSONDecodeError:
                    return response
        except requests.exceptions.RequestException as e:
            logging.getLogger('billing').info(
                'Mb service requests exception: {}. url: {}, data: {}'.format(
                    e, url, data))

        if not getattr(settings, 'TESTS', False):  # pragma: no cover
            time.sleep(settings.MB_TIMEOUT)

    else:
        error_callback()

    return False


def mb_settings(client=None, country=None):
    """
    Get MB_URLS by country code
    """
    return get_settings('MB_URLS', country=country, client=client)


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

    response = _request(
        url=urls['fixtures'].format(client.login),
        data={
            'client_login': client.login,
            'token': urls['token']
        },
        error_callback=_error_callback)
    if response:
        client.refresh_from_db()
        client.url = response.get('url', None)
        client.save()
    return response


def client_install(client):
    """
    Client installation
    """
    logging.getLogger('billing').info(
        'Begin client installation task. Id: {}; login: {}'.format(
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


def client_cache_invalidate(client):
    """
    Client cache invalidate
    """
    logging.getLogger('billing').info(
        'Begin client cache invalidation task. Id: {}; login: {}'.format(
            client.id, client.login))

    urls = mb_settings(client)
    url = urls.get('client_invalidation')

    if not url:
        return True

    def _error_callback():
        logging.getLogger('billing').error(
            'Failed client cache invalidation. Id: {}; login: {}'.format(
                client.id, client.login))

    return _request(
        url=url.format(client.login),
        data={'token': urls['token']},
        error_callback=_error_callback,
    )


def client_login_cache_invalidate(client):
    """
    Invalidate client login/alias cache
    """
    logging.getLogger('billing').info(
        'Begin a client login cache invalidation task. Id: {}; login: {}'.
        format(client.id, client.login))

    urls = mb_settings(client)

    def _error_callback():
        logging.getLogger('billing').error('Client login cache invalidation \
            task is failed. Id: {}; login: {}'.format(client.id, client.login))

    return _request(
        url=urls['login_invalidation'],
        data={
            'client_login': client.login,
            'token': urls['token']
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
        data={
            'client_login': client.login,
            'token': urls['token']
        },
        error_callback=_error_callback)
    if result:
        client.status = 'archived'
        client.save()

    return result
