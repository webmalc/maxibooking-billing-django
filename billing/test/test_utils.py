import pytest

from billing.lib import utils
from clients.models import Client

pytestmark = pytest.mark.django_db


def test_clsfstr():
    assert isinstance(utils.clsfstr('clients.models', 'Client')(), Client)
