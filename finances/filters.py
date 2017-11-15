import rest_framework_filters as filters

from .models import Order


class OrderFilterSet(filters.FilterSet):
    class Meta:
        model = Order
        fields = {
            'status': ['exact'],
            'client_services__service': ['exact'],
            'client_services__id': ['exact'],
            'client__login': ['exact', 'startswith'],
            'expired_date': ['exact', 'gte', 'lte'],
            'paid_date': ['exact', 'gte', 'lte'],
            'created': ['exact', 'gte', 'lte'],
        }
