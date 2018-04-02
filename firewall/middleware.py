from django.core.exceptions import PermissionDenied

from .lib.firewall import Firewall


class FirewallMiddleware(object):
    """
    Firewall middleware
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        firewall = Firewall(request)
        if not firewall.check():
            raise PermissionDenied()
        response = self.get_response(request)
        return response
