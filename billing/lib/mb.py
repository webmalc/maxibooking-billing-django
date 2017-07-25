import logging
import time

import requests
from django.conf import settings
from django.core.urlresolvers import reverse


def install_client(client):
    """
    Client installation
    """
    logging.getLogger('billing').info(
        'Begin client installation. Id: {}; login: {}'.format(client.id,
                                                              client.login))
    i = 0
    while i < 10:
        i += 1
        try:
            response = requests.post(
                settings.MB_URL,
                timeout=20,
                json={
                    'client':
                    client.login,
                    'results_url':
                    reverse('client-install-result', args=[client.login])
                })
            if response.status_code == 200:
                break
        except requests.exceptions.RequestException:
            pass

        if settings.DEBUG:
            time.sleep(settings.MB_TIMEOUT)

    else:
        logging.getLogger('billing').info(
            'Failed client installation. Id: {}; login: {}'.format(
                client.id, client.login))
