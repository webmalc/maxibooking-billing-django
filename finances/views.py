from rest_framework import viewsets

from .models import Price, Service
from .serializers import PriceSerializer, ServiceSerializer


class ServiceViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Service viewset
    """
    queryset = Service.objects.all().select_related(
        'created_by', 'modified_by').prefetch_related('prices')
    search_fields = ('title', 'description', 'id')
    serializer_class = ServiceSerializer
    filter_fields = ('is_enabled', 'period_units', 'created')


class PriceViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Price viewset
    """
    queryset = Price.objects.all().select_related('created_by', 'modified_by',
                                                  'service', 'country')
    search_fields = ('country__name', 'service__title', 'price', 'id')
    serializer_class = PriceSerializer
    filter_fields = ('is_enabled', 'service', 'country')
