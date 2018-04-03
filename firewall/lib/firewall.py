from ..models import Rule
from ..settings import FIREWALL_ALLOW_BY_DEFAULT


class Firewall():
    """
    Firewall core class
    """

    def __init__(self, request):
        self.request = request
        self.rules = Rule.objects.fetch()

    def check(self):
        """
        Check request ip/host against rules
        """

        for rule in self.rules:
            pass
        return FIREWALL_ALLOW_BY_DEFAULT
