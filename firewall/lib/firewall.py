from ipware import get_client_ip

from ..models import Rule
from ..settings import (FIREWALL_ALLOW_BY_DEFAULT, FIREWALL_IPWARE_PROXY_COUNT,
                        FIREWALL_LOGGING_HANDLER)


class Firewall():
    """
    Firewall core class
    """

    def __init__(self, request):
        self.request = request
        self.rules = Rule.objects.fetch()
        self.ip, self.routable = get_client_ip(
            request,
            proxy_count=FIREWALL_IPWARE_PROXY_COUNT,
        )
        self.logger = None
        if FIREWALL_LOGGING_HANDLER:
            import logging
            self.logger = logging.getLogger(FIREWALL_LOGGING_HANDLER)
        self.path = self.request.path

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

        for rule in self.rules:
            pass
        self.logger.info(self.request.path)
        return FIREWALL_ALLOW_BY_DEFAULT
