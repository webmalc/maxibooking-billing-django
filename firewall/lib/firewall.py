from ipware import get_client_ip

from ..models import Rule
from ..settings import (FIREWALL_ALLOW_BY_DEFAULT, FIREWALL_IPWARE_PROXY_COUNT,
                        FIREWALL_LOGGING_HANDLER)


class Firewall():
    """
    Firewall core class
    """

    def __init__(self, request=None, ip=None, path=None):
        if not request and not (ip and path):
            raise ValueError('Empty request and (ip and path)')
        self.request = request
        self.rules = Rule.objects.fetch()
        self.ip = None
        self.logger = None
        if FIREWALL_LOGGING_HANDLER:
            import logging
            self.logger = logging.getLogger(FIREWALL_LOGGING_HANDLER)

        if request:
            self.ip, self.routable = get_client_ip(
                request,
                proxy_count=FIREWALL_IPWARE_PROXY_COUNT,
            )
            self.client_ip = request.GET.get('client_ip', None)
            self.path = self.request.path
        else:
            self.ip = ip
            self.path = path

    def _log(self, message):
        if self.logger:
            self.logger.info(message)

    def check(self):
        """
        Check request ip against rules
        """
        if not self.ip:
            self._log('Can`t get ip. Path: {}'.format(self.request))
            return FIREWALL_ALLOW_BY_DEFAULT

        check = []
        for rule in self.rules:
            check.append(rule.check_ip(self.ip))

        # TODO: check client_ip

        # self.logger.info(self.request.path)
        return FIREWALL_ALLOW_BY_DEFAULT
