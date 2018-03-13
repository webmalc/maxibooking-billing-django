import pytest
from django.core.urlresolvers import reverse
from django.core.validators import ValidationError
from moneyed import EUR, Money

from billing.lib.test import json_contains
from finances.models import Price, Service
from hotels.models import Country


def test_price_list_by_user(client):
    response = client.get(reverse('price-list'))
    assert response.status_code == 401


def test_price_list_by_admin(admin_client, settings):
    response = admin_client.get(reverse('price-list'))
    assert response.status_code == 200
    assert len(response.json()['results']) == 6
    json_contains(response, '234234.00')


def test_price_display_by_user(client):
    response = client.get(reverse('price-detail', args=[7]))
    assert response.status_code == 401


def test_price_display_by_admin(admin_client):
    response = admin_client.get(reverse('price-detail', args=[11]))
    assert response.status_code == 200
    response_json = response.json()
    assert response_json['price'] == '4500.00'
    assert response_json['country'] is None
    assert response_json['is_enabled'] is True
    assert response_json['for_unit'] is False


def test_price_new(admin_client):
    service = Service.objects.get(pk=4)
    country = Country.objects.get(pk=1)
    service.prices.all().delete()

    # SUCCESS: add base price
    price = Price()
    price.service = service
    price.price = Money(120, EUR)
    price.full_clean()
    price.save()

    # ERROR: add another base price
    with pytest.raises(ValidationError) as e:
        price.pk = None
        price.full_clean()
        price.save()
    assert 'Base price for this country already exists' in e.value.messages

    # SUCCESS: add base country price
    price.pk = None
    price.country = country
    price.price = Money(75, EUR)
    price.full_clean()
    price.save()

    # ERROR: add another base price
    with pytest.raises(ValidationError) as e:
        price.pk = None
        price.full_clean()
        price.save()
    assert 'Base price for this country already exists' in e.value.messages
    assert service.prices.all().count() == 2

    # SUCCESS: add base period price 5-10
    price.pk = None
    price.country = None
    price.price = Money(40, EUR)
    price.period_from = 5
    price.period_to = 10
    price.full_clean()
    price.save()

    # ERROR: add another period price 5-10
    with pytest.raises(ValidationError) as e:
        price.pk = None
        price.full_clean()
        price.save()
    assert 'Price with this period already exists' in e.value.messages

    # SUCCESS: add country period price 5-10
    price.pk = None
    price.country = country
    price.price = Money(35, EUR)
    price.full_clean()
    price.save()

    # ERROR: add another period price 6-7
    with pytest.raises(ValidationError) as e:
        price.pk = None
        price.country = None
        price.period_from = 6
        price.period_to = 7
        price.full_clean()
        price.save()
    assert 'Price with this period already exists' in e.value.messages

    # ERROR: add another period price 7-14
    with pytest.raises(ValidationError) as e:
        price.pk = None
        price.country = None
        price.period_from = 7
        price.period_to = 14
        price.full_clean()
        price.save()
    assert 'Price with this period already exists' in e.value.messages

    # ERROR: add another period price 2-7
    with pytest.raises(ValidationError) as e:
        price.pk = None
        price.country = None
        price.period_from = 2
        price.period_to = 7
        price.full_clean()
        price.save()
    assert 'Price with this period already exists' in e.value.messages

    # ERROR: add another period price 10-12
    with pytest.raises(ValidationError) as e:
        price.pk = None
        price.country = None
        price.period_from = 10
        price.period_to = 12
        price.full_clean()
        price.save()
    assert 'Price with this period already exists' in e.value.messages

    # SUCCESS: add base period price 11-∞
    price.pk = None
    price.price = Money(15, EUR)
    price.period_from = 11
    price.period_to = None
    price.full_clean()
    price.save()

    # SUCCESS: add base period price ∞-4
    price.pk = None
    price.price = Money(15, EUR)
    price.period_from = None
    price.period_to = 4
    price.full_clean()
    price.save()

    # ERROR: add another period price 22-33
    with pytest.raises(ValidationError) as e:
        price.pk = None
        price.country = None
        price.period_from = 22
        price.period_to = 33
        price.full_clean()
        price.save()
    assert 'Price with this period already exists' in e.value.messages

    # ERROR: add another period price 1-3
    with pytest.raises(ValidationError) as e:
        price.pk = None
        price.country = None
        price.period_from = 1
        price.period_to = 3
        price.full_clean()
        price.save()
    assert 'Price with this period already exists' in e.value.messages

    # ERROR: add another country period price 5-11
    with pytest.raises(ValidationError) as e:
        price.pk = None
        price.country = country
        price.period_from = 5
        price.period_to = 11
        price.full_clean()
        price.save()
    assert 'Price with this period already exists' in e.value.messages

    # SUCCESS: add another country period price 11-20
    price.pk = None
    price.country = country
    price.price = Money(35, EUR)
    price.period_from = 11
    price.period_to = 20
    price.full_clean()
    price.save()

    assert service.prices.all().count() == 7
