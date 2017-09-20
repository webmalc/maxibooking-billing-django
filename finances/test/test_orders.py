import arrow
import pytest
from django.conf import settings

from ..models import Order

pytestmark = pytest.mark.django_db


def test_order_creation_and_modifications(mailoutbox):
    order = Order()
    order.client_id = 1
    order.save()
    assert order.price == 0
    assert order.status == 'new'
    expired_date = arrow.get(order.created).shift(
        days=+settings.MB_ORDER_EXPIRED_DAYS).floor('second').datetime
    assert arrow.get(order.expired_date).floor('second') == expired_date

    assert len(mailoutbox) == 1
    mail = mailoutbox[0]
    assert 'New order created' in mail.subject
    assert mail.recipients() == ['user@one.com']

    order.client_services.add(1, 2)
    assert float(order.price) == 14001.83
    assert 'Test service two' in order.note
    assert '1999.98' in order.note

    order.note = 'test note'
    order.price = 111.25
    order.save()

    assert float(order.price) == 111.25
    assert order.note == 'test note'

    order.note = None
    order.price = 0
    order.save()
    assert float(order.price) == 14001.83
    assert 'Test service one' in order.note
    assert '12001.85' in order.note
