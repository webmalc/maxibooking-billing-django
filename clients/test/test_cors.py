"""
The test CORS module
"""
import pytest
from django.http import HttpRequest

from clients.models import Client
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
