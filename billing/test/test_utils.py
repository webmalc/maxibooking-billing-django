import pytest

from billing.lib import utils
from clients.models import Client

pytestmark = pytest.mark.django_db


def test_clsfstr():
    assert isinstance(utils.clsfstr('clients.models', 'Client')(), Client)


def test_get_code():
    a, b = utils.get_code('one~two')
    assert a == 'one'
    assert b == 'two'

    a, b = utils.get_code('test')
    assert a == 'test'
    assert b is None

    with pytest.raises(ValueError):
        a, b = utils.get_code('test~cw~er')
