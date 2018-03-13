from django.apps import apps
from django.core.validators import ValidationError
from django.db.models import Q


def validate_price_periods(p):
    # validate default country price
    model = apps.get_model('finances.Price')
    if not p.period_from and not p.period_to:
        prices = model.objects.filter(
            service=p.service,
            country=p.country,
            period_from__isnull=True,
            period_to__isnull=True,
            is_enabled=True,
        ).exclude(id=p.id)
        if prices.exists():
            raise ValidationError('Base price for this country already exists')

    # validate price periods
    if p.period_from or p.period_to:
        prices = model.objects.filter(
            service=p.service,
            country=p.country,
            is_enabled=True,
        ).exclude(id=p.id)
        prices = prices.exclude(
            period_from__isnull=True,
            period_to__isnull=True,
        )
        if p.period_from:
            prices = prices.filter(
                Q(period_to__gte=p.period_from) | Q(period_to__isnull=True))
        if p.period_to:
            prices = prices.filter(
                Q(period_from__lte=p.period_to) | Q(period_from__isnull=True))
        if prices.exists():
            raise ValidationError('Price with this period already exists')
