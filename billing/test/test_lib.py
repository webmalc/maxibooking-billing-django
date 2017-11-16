import pytest

from billing.lib import trans
from finances.models import Order

pytestmark = pytest.mark.django_db


def test_trans_auto_populate(mailoutbox):
    order = Order()
    order.client_id = 1
    order.save()
    order.client_services.add(1, 2)
    trans.auto_populate(order, 'note', order.generate_note)
    assert 'Test service two' in order.note_en
    assert 'Тестовый сервис' in order.note_ru
