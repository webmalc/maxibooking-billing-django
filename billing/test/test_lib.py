import pytest
from billing.lib import lang, trans
from django.utils import translation
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


def test_get_lang(settings):
    assert lang.get_lang() == lang.DEFAULT_LANG
    translation.activate('ru')
    assert lang.get_lang() == 'ru'
    translation.activate(settings.LANGUAGE_CODE)
