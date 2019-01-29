import pytest

from billing.lib.timezone import get_timezone
from hotels.models import City

pytestmark = pytest.mark.django_db


def test_get_timezone():
    chegutu = City.objects.get(name='Chegutu')
    chitungwiza = City.objects.get(name='Chitungwiza')
    assert get_timezone(city=chegutu) == 'Africa/Harare'
    assert get_timezone(city=chitungwiza) == 'Africa/Harare'
    assert get_timezone(55.910839, 37.726389) == 'Europe/Moscow'
    assert get_timezone(55.91, 37.72) == 'Europe/Moscow'
    assert get_timezone(47.283049, -120.760049) == 'America/Los_Angeles'
    assert get_timezone(48.864716, 2.349014) == 'Europe/Paris'
    # test timezone Asia/Qostanay overwrite
    assert get_timezone(53.229647, 63.659657) == 'Asia/Almaty'
