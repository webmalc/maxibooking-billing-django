from rest_framework import viewsets

from .models import Service
from .serializers import ServiceSerializer


class ServiceViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Service viewset
    """
    queryset = Service.objects.all().select_related('created_by',
                                                    'modified_by')
    search_fields = ('title', 'description', 'price', 'id')
    serializer_class = ServiceSerializer
    filter_fields = ('is_enabled', 'period_units', 'created')
