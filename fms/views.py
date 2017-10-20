from rest_framework import viewsets

from .models import Fms, Kpp
from .serializers import FmsSerializer, KppSerializer


class BaseViewSet():
    """
    Base viewset
    """
    search_fields = ('id', 'internal_id', 'name', 'code', 'end_date')
    page_size_query_param = 'page_size'
    max_page_size = 1000


class KppViewSet(viewsets.ReadOnlyModelViewSet, BaseViewSet):
    """
    Kpp viewset
    """
    queryset = Kpp.objects.all()
    serializer_class = KppSerializer
    lookup_field = 'internal_id'


class FmsViewSet(viewsets.ReadOnlyModelViewSet, BaseViewSet):
    """
    Fms viewset
    """
    queryset = Fms.objects.all()
    serializer_class = FmsSerializer
    lookup_field = 'internal_id'
