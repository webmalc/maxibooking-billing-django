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

        for rule in Rule.objects.fetch():
            print(rule)
        return FIREWALL_ALLOW_BY_DEFAULT
