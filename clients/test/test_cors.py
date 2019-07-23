"""
The test CORS module
"""
import pytest
from django.http import HttpRequest
from django.test import TestCase

from clients.models import Client, ClientWebsite
from clients.signals import cors_allow_with_own_domains

pytestmark = pytest.mark.django_db


def test_cors_allow_with_own_domains(mocker):
    """
    Should return True if the request belongs to the one of the client with the
    own domain name
    """
    HttpRequest.get_host = mocker.MagicMock(return_value='invalid.com')
    assert not cors_allow_with_own_domains(None, HttpRequest())

    HttpRequest.get_host = mocker.MagicMock(return_value='hotel.one')
    website = Client.objects.get(pk=1).website
    website.url = 'http://hotel.one'
    website.save()

    assert not cors_allow_with_own_domains(None, HttpRequest())

    website.own_domain_name = True
    website.save()

    assert cors_allow_with_own_domains(None, HttpRequest())

    website.is_enabled = False
    website.save()

    assert not cors_allow_with_own_domains(None, HttpRequest())


def test_cors_allow_domains_from_settings(mocker):
    """
    Should return True if the request belongs to the domains from the settings
    """
    HttpRequest.get_host = mocker.MagicMock(return_value='invalid.com')
    assert not cors_allow_with_own_domains(None, HttpRequest())

    HttpRequest.get_host = mocker.MagicMock(return_value='maxi-booking.com')
    assert cors_allow_with_own_domains(None, HttpRequest())

    HttpRequest.get_host = mocker.MagicMock(return_value='maxi-booking.ru')
    assert cors_allow_with_own_domains(None, HttpRequest())

    HttpRequest.get_host = mocker.MagicMock(return_value='sub.maxi-booking.ru')
    assert cors_allow_with_own_domains(None, HttpRequest())

    HttpRequest.get_host = mocker.MagicMock(return_value='www.maxi-booking.ru')
    assert cors_allow_with_own_domains(None, HttpRequest())


@pytest.mark.usefixtures('mocker')
class CorsTestCase(TestCase):
    """
    The CORS test case
    """

    def test_calc_api_cache(self):
        """
        Check if the cache works with the CORS library
        """
        website = Client.objects.get(pk=1).website
        website.url = 'http://hotel.one'
        website.own_domain_name = True
        website.save()

        with self.assertNumQueries(1):
            ClientWebsite.objects.check_by_own_domain('hotel.one')
        with self.assertNumQueries(1):
            ClientWebsite.objects.check_by_own_domain('hotel.two')
        with self.assertNumQueries(0):
            ClientWebsite.objects.check_by_own_domain('hotel.one')
        with self.assertNumQueries(0):
            ClientWebsite.objects.check_by_own_domain('hotel.two')

        website.own_domain_name = False
        website.save()
        with self.assertNumQueries(1):
            ClientWebsite.objects.check_by_own_domain('hotel.one')
