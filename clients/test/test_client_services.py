import json

import arrow
import pytest
from django.urls import reverse
from moneyed import EUR, Money

from billing.lib.test import json_contains
from clients.managers import ServiceCategoryGroup
from clients.models import Client, ClientService
from clients.tasks import client_services_activation, client_services_update
from finances.lib.calc import Calc
from finances.models import (ClientDiscount, Order, Price, Service,
                             ServiceCategory)

pytestmark = pytest.mark.django_db


def test_client_service_category_group_class():

    cat = ServiceCategory.objects.get(pk=1)
    group = ServiceCategoryGroup(cat)
    service1 = ClientService.objects.get(pk=1)
    service2 = ClientService.objects.get(pk=2)
    group.add_client_services(service1, service2)

    assert len(group.client_services) == 2
    assert group.price == Money(14001.83, EUR)
    assert group.quantity == 7

    service2.pk = None
    service2.service_id = 3
    service2.save()
    service2.refresh_from_db()

    with pytest.raises(ValueError) as e:
        group.add_client_services(service2)

    assert str(e.value) == 'Invalid client_service category'


def test_client_services_list_by_user(client):
    response = client.get(reverse('clientservice-list'))
    assert response.status_code == 401


def test_client_services_list_by_admin(admin_client):
    response = admin_client.get(reverse('clientservice-list'))
    assert response.status_code == 200
    assert len(response.json()['results']) == 5
    json_contains(response, '12001.85')


def test_client_service_display_by_admin(admin_client):
    response = admin_client.get(reverse('clientservice-detail', args=[1]))
    assert response.status_code == 200
    json_contains(response, '1999.98')
    json_contains(response, 'user-one')


def test_client_service_display_by_user(client):
    response = client.get(reverse('clientservice-detail', args=[1]))
    assert response.status_code == 401


def test_client_service_create_invalid_by_admin(admin_client):
    data = {
        'quantity': -3,
        'client': 'invalid-user',
        'service': 312,
        'begin': arrow.utcnow().shift(days=-1).isoformat(),
        'end': arrow.utcnow().shift(days=-3).isoformat()
    }
    url = reverse('clientservice-list')
    response = admin_client.post(
        url, data=json.dumps(data), content_type="application/json")
    response_json = response.json()

    assert response_json['quantity'] == [
        'Ensure this value is greater than or equal to 1.'
    ]
    assert response_json['service'] == [
        'Invalid pk "312" - object does not exist.'
    ]
    assert response_json['client'] == [
        'Object with login=invalid-user does not exist.'
    ]

    data['quantity'] = 2
    data['client'] = 'user-one'
    data['service'] = 1
    response = admin_client.post(
        url, data=json.dumps(data), content_type="application/json")
    response_json = response.json()

    #     assert response_json['non_field_errors'] == [
    #         'The fields client, is_enabled, service, \
    # quantity must make a unique set.'
    #     ]

    data['service'] = 3
    response = admin_client.post(
        url, data=json.dumps(data), content_type="application/json")
    response_json = response.json()

    assert response_json['non_field_errors'] == ['Please correct dates.']

    data['begin'] = arrow.utcnow().shift(days=1).isoformat()
    response = admin_client.post(
        url, data=json.dumps(data), content_type="application/json")
    response_json = response.json()

    assert response_json['non_field_errors'] == ['Please correct dates.']

    data['end'] = arrow.utcnow().shift(months=+3).isoformat()
    response = admin_client.post(
        reverse('clientservice-list'),
        data=json.dumps(data),
        content_type="application/json")
    response_json = response.json()
    assert response_json['non_field_errors'] == ['Empty service prices.']


def test_client_service_create_by_admin(admin_client):
    client = Client.objects.get(login='user-one')

    assert client.restrictions.rooms_limit != 5

    data = {'quantity': 5, 'client': client.login, 'service': 2}
    url = reverse('clientservice-list')
    response = admin_client.post(
        url, data=json.dumps(data), content_type="application/json")
    response_json = response.json()

    assert response_json['price'] == '17500.00'
    assert response_json['client'] == client.login
    assert response_json['is_enabled'] is True
    assert response_json['country'] == 'us'
    assert response_json['status'] == 'active'

    client = Client.objects.get(login='user-one')
    assert client.restrictions.rooms_limit == 5

    begin = arrow.utcnow()
    end = begin.shift(years=+1)
    format = '%d.%m.%Y %H:%I'
    assert arrow.get(response_json['begin']).datetime.strftime(
        format) == begin.datetime.strftime(format)
    assert arrow.get(response_json['end']).datetime.strftime(
        format) == end.datetime.strftime(format)


def test_client_services_update_active_task(admin_client):
    end = arrow.utcnow().shift(days=+5)
    service_rooms = Service.objects.get(pk=1)
    service_other = Service.objects.get(pk=3)
    service_other.period = 1
    service_other.save()

    client_service = ClientService()
    client_service.quantity = 2
    client_service.begin = arrow.utcnow().shift(months=-1).datetime
    client_service.end = end.datetime
    client_service.service = service_rooms
    client_service.client_id = 4
    client_service.is_paid = True
    client_service.save()

    Price.objects.create(price=Money(1000, EUR), service=service_other)
    client_service_other = ClientService()
    client_service_other.quantity = 2
    client_service_other.begin = client_service.begin
    client_service_other.end = client_service.end
    client_service_other.service = service_other
    client_service_other.client_id = 4
    client_service_other.is_paid = True
    client_service_other.save()

    assert client_service.price == Calc.factory(client_service).calc()
    price = service_rooms.prices.get(pk=8)
    price.price = Money(2500, EUR)
    price.save()

    client_services_update.delay()
    client_service.refresh_from_db()

    # assert client_service.status == 'processing'
    assert client_service.is_paid is False
    assert client_service.end == end.shift(months=+3).datetime
    assert client_service.price == Money(5000, EUR)

    order = Order.objects.get(
        client__pk=4, client_services__pk=client_service.pk)
    assert order.price == Money(7000, EUR)
    assert order.status == 'new'
    assert order.client_services.count() == 2

    client_services_update.delay()
    orders = Order.objects.filter(
        client__pk=4, client_services__pk=client_service.pk)
    assert orders.count() == 1


def test_client_services_update_with_discount(admin_client, discounts):
    end = arrow.utcnow().shift(days=+5)
    service_rooms = Service.objects.get(pk=1)
    service_other = Service.objects.get(pk=3)
    service_other.period = 1
    service_other.save()

    client_service = ClientService()
    client_service.quantity = 2
    client_service.begin = arrow.utcnow().shift(months=-1).datetime
    client_service.end = end.datetime
    client_service.service = service_rooms
    client_service.client_id = 4
    client_service.is_paid = True
    client_service.save()

    discount = discounts[0]
    discount.percentage_discount = 15.5
    discount.save()
    ClientDiscount.client_spanshot(discount, client_service.client)

    Price.objects.create(price=Money(1000, EUR), service=service_other)
    client_service_other = ClientService()
    client_service_other.quantity = 2
    client_service_other.begin = client_service.begin
    client_service_other.end = client_service.end
    client_service_other.service = service_other
    client_service_other.client_id = 4
    client_service_other.is_paid = True
    client_service_other.save()

    assert client_service.price == Calc.factory(client_service).calc()
    price = service_rooms.prices.get(pk=8)
    price.price = Money(2500, EUR)
    price.save()

    client_services_update.delay()
    client_service.refresh_from_db()

    assert client_service.is_paid is False
    assert client_service.end == end.shift(months=+3).datetime
    assert client_service.price == Money(5000, EUR)

    order = Order.objects.get(
        client__pk=4, client_services__pk=client_service.pk)

    assert order.price == Money(5915, EUR)
    assert order.status == 'new'
    assert order.client_services.count() == 2


def test_client_services_update_next_task(admin_client):
    end = arrow.utcnow().shift(months=2)
    service = Service.objects.get(pk=1)
    client_service = ClientService()
    client_service.quantity = 2
    client_service.begin = arrow.utcnow().shift(days=10).datetime
    client_service.end = end.datetime
    client_service.service = service
    client_service.client_id = 4
    client_service.status = 'next'
    client_service.is_paid = False
    client_service.save()

    assert client_service.price == Calc.factory(client_service).calc()
    price = service.prices.get(pk=8)
    price.price = Money(2500, EUR)
    price.save()

    client_services_update.delay()
    client_service.refresh_from_db()

    assert client_service.is_paid is False
    assert client_service.end == end
    assert client_service.price == Money(5000, EUR)

    order = Order.objects.get(
        client__pk=4, client_services__pk=client_service.pk)
    assert order.price == Money(5000, EUR)
    assert order.status == 'new'

    client_services_update.delay()
    orders = Order.objects.filter(
        client__pk=4, client_services__pk=client_service.pk)

    assert orders.count() == 1


def test_client_services_default_dates(admin_client):
    prev_client_service = ClientService.objects.get(pk=1)
    prev_client_service.end = arrow.utcnow().shift(days=4).datetime
    prev_client_service.save()

    assert prev_client_service.is_enabled is True
    data = {'quantity': 1, 'client': 'user-one', 'service': 4}
    url = reverse('clientservice-list')
    response = admin_client.post(
        url, data=json.dumps(data), content_type="application/json")

    assert response.status_code == 201
    prev_client_service.refresh_from_db()
    assert prev_client_service.is_enabled is False
    next_client_service = ClientService.objects.get(service__pk=4)

    assert next_client_service.begin == prev_client_service.end


def test_client_services_activation_task(admin_client, make_orders):
    order = Order.objects.get(pk=1)
    client_service = ClientService.objects.get(pk=2)
    client = client_service.client
    client.services.all().delete()
    client.services.add(client_service)
    client_service.begin = arrow.utcnow().shift(days=2).datetime
    client_service.status = 'next'
    client_service.save()
    order.client_services.add(1, 2, client_service)
    order.set_paid('bill')
    client_service.refresh_from_db()

    assert client_service.is_paid is True
    assert client_service.status == 'next'

    client_services_activation.delay()
    client_service.refresh_from_db()

    assert client_service.is_paid is True
    assert client_service.status == 'next'
    assert client.restrictions.rooms_limit == 0

    client_service.begin = arrow.utcnow().shift(days=-2).datetime
    client_service.save()
    client_services_activation.delay()
    client_service.refresh_from_db()
    client.restrictions.refresh_from_db()

    assert client_service.is_paid is True
    assert client_service.status == 'active'
    assert client.restrictions.rooms_limit == 5
