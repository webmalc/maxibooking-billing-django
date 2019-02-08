import pytest

from billing.lib import mb
from clients.models import Client

pytestmark = pytest.mark.django_db


def test_get_parsed_client_urls_without_url():
    urls = mb.get_parsed_client_urls(Client.objects.get(pk=1))
    assert urls['install'] == 'http://example.com'
    assert urls['fixtures'] is None


def test_get_parsed_client_urls():
    client = Client.objects.get(pk=1)
    client.url = 'http://google.com'
    client.save()

    urls = mb.get_parsed_client_urls(client)
    assert urls['install'] == 'http://example.com'
    assert urls['fixtures'] == 'http://google.com/fixtures'
