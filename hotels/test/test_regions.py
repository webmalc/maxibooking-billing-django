from django.core.urlresolvers import reverse

from billing.lib.test import json_contains


def test_region_list_by_user(client):
    response = client.get(reverse('region-list'))
    assert response.status_code == 401


def test_regions_list_by_admin(admin_client):
    response = admin_client.get(reverse('region-list'))
    assert response.status_code == 200
    assert len(response.json()['results']) == 7
    json_contains(response, 'Masvingo')


def test_regions_display_by_admin(admin_client):
    response = admin_client.get(reverse('region-detail', args=[3]))
    assert response.status_code == 200
    json_contains(response, 'Mashonaland East')


def test_regions_display_by_user(client):
    response = client.get(reverse('region-detail', args=[3]))
    assert response.status_code == 401
