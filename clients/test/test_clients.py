import json

from django.core.urlresolvers import reverse
from moneyed import EUR, Money

from billing.lib import mb
from billing.lib.test import json_contains
from finances.models import Service
from hotels.models import Property, Room

from ..models import Client
from ..tasks import client_archivation


def test_clients_list_by_user(client):
    response = client.get(reverse('client-list'))
    assert response.status_code == 401


def test_clients_list_by_admin(admin_client):
    response = admin_client.get(reverse('client-list'))
    assert response.status_code == 200
    assert len(response.json()['results']) == 6
    json_contains(response, 'User Two')


def test_client_display_by_user(client):
    response = client.get(reverse('client-detail', args=['user-three']))
    assert response.status_code == 401


def test_client_display_by_admin(admin_client):
    response = admin_client.get(reverse('client-detail', args=['user-three']))
    assert response.status_code == 200
    json_contains(response, 'user@three.com')


def test_client_create_invalid_by_admin(admin_client):
    data = json.dumps({'login': 'invalid login', 'email': 'user@one.com'})
    response = admin_client.post(
        reverse('client-list'), data=data, content_type="application/json")
    response_json = response.json()

    assert response_json['login'] == [
        'Enter a valid login. This value may \
contain only lowercase letters, numbers, and "-" character.'
    ]
    assert response_json['email'] == [
        'client with this e-mail already exists.'
    ]
    assert response_json['phone'] == ['This field is required.']


def test_client_create_by_admin(admin_client):
    data = json.dumps({
        'login': 'new-user',
        'email': 'new@user.mail',
        'name': 'New User',
        'phone': '+79239999999',
        'country': 'af'
    })
    response = admin_client.post(
        reverse('client-list'), data=data, content_type="application/json")
    response_json = response.json()

    assert response_json['login'] == 'new-user'
    assert response_json['status'] == 'not_confirmed'
    assert response_json['created_by'] == 'admin'

    response = admin_client.get(reverse('client-list'))
    assert len(response.json()['results']) == 7
    json_contains(response, 'new@user.mail')


def test_client_confirm_by_user(client):
    response = client.post(
        reverse('client-confirm', args=['new-user']),
        content_type="application/json")
    assert response.status_code == 401


def test_client_confirm_by_admin(admin_client):
    response = admin_client.post(
        reverse('client-confirm', args=['user-three']),
        content_type="application/json")

    assert response.json()['status'] is True
    client = Client.objects.get(login='user-three')
    assert client.status == 'active'


def test_client_fixtures_by_user(client):
    response = client.post(
        reverse('client-fixtures', args=['user-three']),
        content_type="application/json")
    assert response.status_code == 401


def test_client_not_installed_fixtures_by_admin(admin_client):
    response = admin_client.post(
        reverse('client-fixtures', args=['user-one']),
        content_type="application/json")
    assert response.json()['status'] is False
    assert response.json()['message'] == 'client not installed'


def test_client_process_fixtures_by_admin(admin_client):
    response = admin_client.post(
        reverse('client-fixtures', args=['user-four']),
        content_type="application/json")
    assert response.json()['status'] is False
    assert response.json()['message'] == 'client installation in process'


def test_client_invalid_fixtures_by_admin(admin_client, settings, mailoutbox):
    settings.MB_URLS['__all__']['fixtures'] = 'http://invalid-domain-name.com'
    response = admin_client.post(
        reverse('client-fixtures', args=['user-two']),
        content_type="application/json")

    assert response.json()['status'] is False
    assert len(mailoutbox) == 2

    mail = mailoutbox[0]

    assert 'Failed client fixtures installation' in mail.subject
    assert 'user-two' in mail.body

    assert 'failed' in mailoutbox[1].subject


def test_client_fixtures_by_admin(admin_client, mocker):
    mb.client_fixtures = mocker.MagicMock(return_value={
        'url': 'test url',
    })
    response = admin_client.post(
        reverse('client-fixtures', args=['user-two']),
        content_type="application/json")
    assert response.json()['status'] is True
    assert response.json()['message'] == 'client fixtures installed'
    assert response.json()['url'] == 'test url'


def test_client_install_by_user(client):
    response = client.post(
        reverse('client-install', args=['user-three']),
        content_type="application/json")
    assert response.status_code == 401


def test_client_install_by_admin(admin_client):
    response = admin_client.post(
        reverse('client-install', args=['user-three']),
        content_type="application/json")

    assert response.json()['status'] is True
    client = Client.objects.get(login='user-three')
    assert client.installation == 'process'


def test_client_failed_install_by_admin(admin_client, settings, mailoutbox):
    settings.MB_URLS['__all__']['install'] = 'http://invalid-domain-name.com'
    response = admin_client.post(
        reverse('client-install', args=['user-one']),
        content_type="application/json")

    assert response.json()['status'] is True
    client = Client.objects.get(login='user-one')
    assert client.installation == 'not_installed'
    assert len(mailoutbox) == 2

    mail = mailoutbox[0]

    assert 'Failed client installation' in mail.subject
    assert 'user-one' in mail.body

    assert 'failed' in mailoutbox[1].subject


def test_client_already_installed_install_by_admin(admin_client):
    response = admin_client.post(
        reverse('client-install', args=['user-two']),
        content_type="application/json")

    assert response.json()['status'] is False


def test_client_install_results_by_client(client):
    response = client.post(
        reverse('client-install-result', args=['user-four']),
        content_type="application/json")

    assert response.status_code == 401


def test_client_install_results_invalid_by_admin(admin_client):
    response = admin_client.post(
        reverse('client-install-result', args=['user-one']),
        content_type="application/json")

    assert response.json()['status'] is False


def test_client_install_results_by_admin(admin_client, mailoutbox):
    data = json.dumps({
        'status': True,
        'password': '123456',
        'url': 'http://example.com'
    })
    response = admin_client.post(
        reverse('client-install-result', args=['user-one']),
        data=data,
        content_type="application/json")

    assert response.json()['status'] is True

    client = Client.objects.get(login='user-one')
    assert client.installation == 'installed'

    mail = mailoutbox[0]
    html = mail.alternatives[0][0]
    assert 'successefull' in mail.subject
    assert '123456' in html
    assert 'http://example.com' in html
    assert client.login in html


def test_client_install_fail_results_by_admin(admin_client, mailoutbox):
    data = json.dumps({'status': False, 'password': None, 'url': None})
    response = admin_client.post(
        reverse('client-install-result', args=['user-one']),
        data=data,
        content_type="application/json")

    assert response.json()['status'] is False

    client = Client.objects.get(login='user-one')
    assert client.installation == 'not_installed'

    mail = mailoutbox[0]
    assert 'failed' in mail.subject


def test_client_trial_by_client(client):
    response = client.post(
        reverse('client-trial', args=['user-three']),
        content_type="application/json")

    assert response.status_code == 401


def test_admin_trial_invalid_by_admin(admin_client, mailoutbox):
    response = admin_client.post(
        reverse('client-trial', args=['user-three']),
        content_type="application/json")
    response_json = response.json()
    assert response_json['status'] is False
    assert response_json[
        'message'] == 'trial activation failed: client already has services'

    mail = mailoutbox[0]

    assert 'Failed client installation' in mail.subject
    assert 'user-three' in mail.body

    response = admin_client.post(
        reverse('client-trial', args=['user-four']),
        content_type="application/json")
    response_json = response.json()
    assert response_json['status'] is False
    assert response_json[
        'message'] == 'trial activation failed: client confirmed'

    response = admin_client.post(
        reverse('client-trial', args=['user-five']),
        content_type="application/json")

    response_json = response.json()
    assert response_json['status'] is False
    assert response_json['message'] == \
        'trial activation failed: default rooms service not found'

    Service.objects.filter(pk=2, type='rooms').update(is_default=True)
    response = admin_client.post(
        reverse('client-trial', args=['user-five']),
        content_type="application/json")

    response_json = response.json()
    assert response_json['status'] is False
    assert response_json['message'] == \
        'trial activation failed: invalid default service: Test service two'


def test_admin_trial_by_admin(admin_client):
    Service.objects.filter(pk=2, type='rooms').update(is_default=True)
    Property.objects.create(
        name='Test property four',
        url='http://property.five',
        client_id=5,
        city_id=1)
    Room.objects.create(name='Test room one', property_id=4, rooms=13)
    Room.objects.create(name='Test room another', property_id=2, rooms=23)
    Property.objects.create(
        name='Test property five',
        url='http://property.six',
        client_id=5,
        city_id=2)
    Room.objects.create(name='Test room two', property_id=5, rooms=12)
    response = admin_client.post(
        reverse('client-trial', args=['user-five']),
        content_type="application/json")

    response_json = response.json()
    assert response_json['status'] is True
    assert response_json['message'] == 'trial successfully activated'

    client = Client.objects.get(pk=5)

    assert client.services.count() == 2
    assert client.rooms_limit == 25
    assert client.services.get(service__type='rooms').price == Money(
        87500.0, EUR)
    assert client.services.get(service__type='connection').status == 'active'


def test_clients_archivation(admin_client):
    client_archivation.delay()
    client = Client.objects.get(login='user-six')
    assert client.status == 'archived'


def test_clients_archivation_invalid(admin_client, settings):
    settings.MB_URLS['__all__']['archive'] = 'http://invalid-domain-name.com'
    client_archivation.delay()
    client = Client.objects.get(login='user-six')
    assert client.status == 'disabled'
