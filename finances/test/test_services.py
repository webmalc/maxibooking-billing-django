import pytest

from ..models import Service


@pytest.mark.django_db
def test_service_period_days():
    service = Service.objects.get(pk=1)
    assert service.period_days == 93
    service.period = 5
    service.save()
    assert service.period_days == 155
