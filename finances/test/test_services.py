import pytest
from django.core.urlresolvers import reverse

from billing.lib.test import json_contains

from ..models import Service


@pytest.mark.django_db
def test_service_period_days():
    service = Service.objects.get(pk=1)
    assert service.period_days == 93
    service.period = 5
    service.save()
    assert service.period_days == 155


def test_services_list_by_user(client):
    response = client.get(reverse('service-list'))
    assert response.status_code == 401


def test_service_list_by_admin(admin_client):
    response = admin_client.get(reverse('service-list'))
    assert response.status_code == 200
    assert len(response.json()['results']) == 3
    json_contains(response, 'Test service three')


def test_service_display_by_admin(admin_client):
    response = admin_client.get(reverse('service-detail', args=[2]))
    assert response.status_code == 200
    json_contains(response, 'Test service two')


def test_service_display_by_user(client):
    response = client.get(reverse('service-detail', args=[2]))
    assert response.status_code == 401
