"""
The Clients CORS module
"""
from corsheaders.middleware import CorsMiddleware

from clients.models import ClientWebsite


def check_host(host: str) -> bool:
    """
    Check if the host is allowed
    """
    middleware = CorsMiddleware()
    if middleware.regex_domain_match(host):
        return True

    return ClientWebsite.objects.check_by_own_domain(host)
