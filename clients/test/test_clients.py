import json

import arrow
import pytest
from django.conf import settings
from django.core.urlresolvers import reverse
from moneyed import EUR, Money

from billing.lib import mb
from billing.lib.test import json_contains
from finances.models import Order, Price, Service
from hotels.models import Property, Room

from ..models import Client
from ..tasks import client_archivation

pytestmark = pytest.mark.django_db


@pytest.fixture
def service():
    service = Service.objects.create(
        title='Temp service',
        type='rooms',
        period=3,
        category_id=1,
        period_units='month',
    )
    Price.objects.create(service=service, price=Money(1233, EUR))

    return service


def test_clients_list_by_user(client):
    response = client.get(reverse('client-list'))
    assert response.status_code == 401


def test_clients_list_by_admin(admin_client):
    response = admin_client.get(reverse('client-list'))
    assert response.status_code == 200
    assert len(response.json()['results']) == 7
    json_contains(response, 'User Two')


def test_client_display_by_user(client):
    response = client.get(reverse('client-detail', args=['user-three']))
    assert response.status_code == 401


def test_client_display_by_admin(admin_client):
    response = admin_client.get(reverse('client-detail', args=['user-three']))
    assert response.status_code == 200
    json_contains(response, 'user@three.com')


def test_client_create_invalid_by_admin(admin_client):
    data = json.dumps({'login': '_amazonses', 'email': 'user@one.com'})
    response = admin_client.post(
        reverse('client-list'), data=data, content_type="application/json")
    response_json = response.json()

    assert response_json['login'] == [
        'Enter a valid domain. This value may \
contain only lowercase letters, numbers, and "-" character.',
        'invalid client login: ' +
        ', '.join(settings.MB_CLIENT_LOGIN_RESTRICTIONS)
    ]
    assert response_json['email'] == [
        'client with this e-mail already exists.'
    ]


def test_client_create_by_admin(admin_client):
    data = json.dumps({
        'login': 'new-user',
        'email': 'new@user.mail',
        'name': 'New User',
        'phone': '+79239999999',
        'country': 'af',
        'postal_code': '123456',
        'address': 'test address',
        'ru': {
            'passport_serial': '1' * 4,
            'passport_number': '1' * 6,
            'passport_date': '2017-12-01T10:22:48.995041Z',
            'passport_issued_by': 'issued by',
            'inn': '1' * 10,
        }
    })
    response = admin_client.post(
        reverse('client-list'), data=data, content_type="application/json")
    response_json = response.json()

    assert response_json['login'] == 'new-user'
    assert response_json['status'] == 'not_confirmed'
    assert response_json['created_by'] == 'admin'
    assert response_json['postal_code'] == '123456'
    assert response_json['address'] == 'test address'
    assert response_json['ru']['passport_serial'] == '1111'

    response = admin_client.get(reverse('client-list'))
    assert len(response.json()['results']) == 8
    json_contains(response, 'new@user.mail')


def test_client_tariff_update_by_user(client):
    response = client.post(
        reverse('client-tariff-update', args=['user-one']),
        content_type="application/json")
    assert response.status_code == 401


def _update_tariff(rooms, period, admin_client):
    data = json.dumps({'rooms': rooms, 'period': period})
    response = admin_client.post(
        reverse('client-tariff-update', args=['user-four']),
        content_type="application/json",
        data=data,
    )
    response_json = response.json()
    assert response.status_code == 200
    assert response_json['status'] is True
    assert response_json['message'] == 'client services successfully updated'

    return response


def test_client_tariff_detail_by_user(client):
    response = client.post(
        reverse('client-tariff-detail', args=['user-one']),
        content_type="application/json")
    assert response.status_code == 401


def test_client_tariff_detail_by_admin(admin_client, service):
    client = Client.objects.get(login='user-four')
    now = arrow.utcnow().format('YYYY-MM-DD')
    next_begin = arrow.utcnow().shift(months=3).format('YYYY-MM-DD')
    _update_tariff(25, 3, admin_client)
    response = admin_client.get(
        reverse('client-tariff-detail', args=['user-four']),
        content_type="application/json")
    assert response.status_code == 200
    response_json = response.json()

    next_tariff = response_json['next']
    assert next_tariff['title'] == 'Test category 1'
    assert next_tariff['rooms'] == 25
    assert now in next_tariff['begin']

    client.services.update(status='active')
    _update_tariff(44, 3, admin_client)
    response = admin_client.get(
        reverse('client-tariff-detail', args=['user-four']),
        content_type="application/json")

    response_json = response.json()

    next_tariff = response_json['next']
    current_tariff = response_json['main']
    assert current_tariff['rooms'] == 25
    assert next_tariff['rooms'] == 44
    assert now in current_tariff['begin']
    assert next_begin in next_tariff['begin']


def test_client_tariff_update_invalid_by_admin(admin_client):
    response = admin_client.post(
        reverse('client-tariff-update', args=['user-five']),
        content_type="application/json")
    assert response.json()['status'] is False
    assert response.json()['message'] == 'invalid client'

    response = admin_client.post(
        reverse('client-tariff-update', args=['user-four']),
        content_type="application/json")

    assert response.json()['status'] is False
    assert response.json()['message'] == 'invalid request'

    data = json.dumps({'rooms': 34, 'period': 5})
    response = admin_client.post(
        reverse('client-tariff-update', args=['user-four']),
        content_type="application/json",
        data=data,
    )
    assert response.json()['status'] is False
    assert response.json()[
        'message'] == 'failed update. Error: connection service not found'


def test_client_tariff_update_by_admin(admin_client, service):
    format = '%d.%m.%Y %H:%I'
    client = Client.objects.get(login='user-four')

    _update_tariff(34, 3, admin_client)
    client.refresh_from_db()
    assert client.services.count() == 2
    assert client.services.get(service__type='rooms').quantity == 24

    client.services.update(status='active')
    _update_tariff(44, 3, admin_client)
    assert client.services.count() == 4
    assert client.services.filter(status='next').count() == 2
    assert client.services.get(
        status='next', service__type='rooms').quantity == 34

    next_rooms = client.services.get(status='next', service__type='rooms')
    prev_rooms = client.services.get(status='active', service__type='rooms')
    begin = next_rooms.begin
    assert begin.strftime(format) == prev_rooms.end.strftime(format)

    _update_tariff(12, 3, admin_client)
    assert client.services.count() == 6
    assert client.services.filter(status='next', is_enabled=True).count() == 2
    next_rooms = client.services.get(
        status='next',
        service__type='rooms',
        is_enabled=True,
    )
    assert begin.strftime(format) == next_rooms.begin.strftime(format)
    assert next_rooms.quantity == 2

    _update_tariff(5, 3, admin_client)
    assert client.services.count() == 7
    assert client.services.filter(status='next', is_enabled=True).count() == 1
    assert client.services.filter(is_enabled=True).count() == 1

    _update_tariff(12, 3, admin_client)
    assert client.services.count() == 9
    assert client.services.filter(status='next', is_enabled=True).count() == 2
    next_rooms = client.services.get(
        status='next',
        service__type='rooms',
        is_enabled=True,
    )
    assert begin.strftime(format) == next_rooms.begin.strftime(format)
    assert next_rooms.quantity == 2

    service_rooms_year = Service.objects.create(
        title='Temp service rooms year',
        type='rooms',
        period=12,
        category_id=1,
        period_units='month',
    )
    service_connection_year = Service.objects.create(
        title='Temp service connection year',
        type='connection',
        period=12,
        category_id=1,
        period_units='month',
    )
    Price.objects.create(service=service_rooms_year, price=Money(233, EUR))
    Price.objects.create(
        service=service_connection_year, price=Money(1500, EUR))

    _update_tariff(22, 12, admin_client)
    next_services = client.services.filter(status='next', is_enabled=True)
    assert next_services.count() == 2
    next_rooms = client.services.get(
        status='next',
        service__type='rooms',
        is_enabled=True,
    )
    assert next_rooms.quantity == 22
    assert begin.strftime(format) == next_rooms.begin.strftime(format)
    client.restrictions_update()
    assert client.restrictions.rooms_limit == 34

    next_services.update(begin=arrow.utcnow().shift(days=-3).datetime)
    order = Order()
    order.price = Money(123, EUR)
    order.status = 'new'
    order.client = client
    order.expired_date = arrow.utcnow().shift(months=4).datetime
    order.save()
    order.client_services.add(*next_services.all())
    order.refresh_from_db()
    order.status = 'paid'
    order.save()

    client.refresh_from_db()

    assert client.services.filter(status='active').count() == 2
    assert client.restrictions.rooms_limit == 22

    client.services.exclude(status='active').delete()
    client.services.filter(service__type='rooms').delete()
    _update_tariff(22, 3, admin_client)

    prev_service = client.services.filter(status='active').first()
    next_services = client.services.filter(status='next', is_enabled=True)
    for next_service in next_services:
        assert prev_service.end == next_service.begin


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
    settings.MB_URLS['__all__'][
        'fixtures'] = 'http://{}.invalid-domain-name.com'
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
        'token': 'test token',
    })
    response = admin_client.post(
        reverse('client-fixtures', args=['user-two']),
        content_type="application/json")
    response_json = response.json()
    assert response_json['status'] is True
    assert response_json['message'] == 'client fixtures installed'
    assert response_json['url'] == 'test url'
    assert response_json['token'] == 'test token'


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
    assert client.url == 'http://example.com'

    mail = mailoutbox[0]
    html = mail.alternatives[0][0]
    assert 'successefull' in mail.subject
    assert '123456' in html
    assert 'http://example.com' in html
    # assert client.login in html
    assert 'admin' in html


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

    assert 'Failed client trial installation' in mail.subject
    assert 'user-three' in mail.body

    response = admin_client.post(
        reverse('client-trial', args=['user-five']),
        content_type="application/json")

    response_json = response.json()
    assert response_json['status'] is False
    assert response_json['message'] == \
        'trial activation failed: default rooms service not found'

    # TODO: fix test
    # Service.objects.filter(pk=2, type='rooms').update(is_default=True)
    # response = admin_client.post(
    #     reverse('client-trial', args=['user-five']),
    #     content_type="application/json")

    # response_json = response.json()
    # assert response_json['status'] is False
    # assert response_json['message'] == \
    #     'trial activation failed: invalid default service: Test service two'


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
    client = Client.objects.get(pk=5)
    assert client.trial_activated is False
    response = admin_client.post(
        reverse('client-trial', args=['user-five']),
        content_type="application/json")

    response_json = response.json()
    assert response_json['status'] is True
    assert response_json['message'] == 'trial successfully activated'

    connection_service = client.services.get(
        service__type='connection',
        status='active',
        is_enabled=True,
    )
    rooms_service = client.services.get(
        service__type='rooms',
        status='active',
        is_enabled=True,
    )

    client.refresh_from_db()
    assert client.services.count() == 2
    assert client.trial_activated is True

    assert client.restrictions.rooms_limit == 25
    assert rooms_service.price == Money(52500.0, EUR)
    assert rooms_service.quantity == 15
    assert connection_service.status == 'active'
    assert connection_service.service.default_rooms == 10


def test_clients_archivation(admin_client):
    client_archivation.delay()
    client = Client.objects.get(login='user-six')
    assert client.status == 'archived'


def test_clients_archivation_invalid(admin_client, settings):
    settings.MB_URLS['__all__']['archive'] = 'http://invalid-domain-name.com'
    client_archivation.delay()
    client = Client.objects.get(login='user-six')
    assert client.status == 'disabled'


def test_client_check_status():
    client = Client.objects.get(login='user-six')
    client.check_status()
    assert client.status == 'active'


def test_client_restrictions_update():
    client = Client.objects.get(login='user-two')
    assert client.restrictions.rooms_limit == 15

    client.restrictions_update(rooms=125)
    assert client.restrictions.rooms_limit == 125

    client.restrictions_update()
    assert client.restrictions.rooms_limit == 15


def test_client_ru_fields_update(admin_client):
    data = json.dumps({
        'ru': {
            'passport_serial': '1' * 4,
            'passport_number': '1' * 6,
            'passport_date': '2017-12-01T10:22:48.995041Z',
            'passport_issued_by': 'issued by',
            'inn': '1' * 10,
        }
    })
    response = admin_client.patch(
        reverse('client-detail', args=['user-two']),
        data=data,
        content_type="application/json")

    assert response.status_code == 200
    response_json = response.json()

    assert response_json['ru']['passport_issued_by'] == 'issued by'

    response = admin_client.patch(
        reverse('client-detail', args=['user-two']),
        data=json.dumps({
            'ru': None
        }),
        content_type="application/json")

    assert getattr(Client.objects.get(login='user-two'), 'ru', None) is None


def test_client_language():
    assert Client.objects.get(login='user-rus').language == 'ru'
    assert Client.objects.get(login='user-one').language == 'en'


def test_client_by_logins(make_orders):
    assert Client.objects.get_by_orders(True).count() == 1
    assert Client.objects.get_by_orders(False).count() == 6

    Order.objects.update(status='new')

    assert Client.objects.get_by_orders(True).count() == 0
    assert Client.objects.get_by_orders(False).count() == 7
