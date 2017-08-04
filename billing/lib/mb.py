import logging
import time

import requests
from django.conf import settings
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from .messengers.mailer import Mailer


def install_client(client):
    """
    Client installation
    """
    logging.getLogger('billing').info(
        'Begin client installation. Id: {}; login: {}'.format(client.id,
                                                              client.login))
    for i in range(0, 10):
        try:
            response = requests.post(
                settings.MB_URL,
                timeout=settings.MB_TIMEOUT,
                json={
                    'client_login':
                    client.login,
                    'token':
                    settings.MB_TOKEN,
                    'results_url':
                    reverse('client-install-result', args=[client.login])
                })
            if response.status_code == 200:
                return True
        except requests.exceptions.RequestException:
            pass

        if settings.DEBUG:
            time.sleep(settings.MB_TIMEOUT)

    else:
        logging.getLogger('billing').error(
            'Failed client installation. Id: {}; login: {}'.format(
                client.id, client.login))
        Mailer.mail_managers(
            subject=_('Failed client installation'),
            template='emails/base_manager.html',
            data={
                'text':
                '{}: {}'.format(_('Failed client installation'), client.login)
            })
        Mailer.mail_client(
            subject=_('Registation failed'),
            template='emails/registration_fail.html',
            data={},
            client=client)

    return False
