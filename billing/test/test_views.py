import pytest
from django.core.urlresolvers import reverse


def test_admin_view_by_admin(admin_client):
    response = admin_client.get(reverse('admin:index'))
    assert response.status_code == 200


def test_admin_view_by_user(client):
    response = client.get(reverse('admin:index'))
    assert response.status_code == 302
