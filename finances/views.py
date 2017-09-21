from rest_framework import viewsets
from rest_framework.decorators import detail_route
from rest_framework.response import Response

from .models import Order, Price, Service
from .serializers import OrderSerializer, PriceSerializer, ServiceSerializer


class OrderViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Order viewset
    """
    queryset = Order.objects.all().select_related(
        'created_by', 'modified_by',
        'client').prefetch_related('client_services')
    search_fields = ('=id', '=client_services__id',
                     'client_services__service__title',
                     'client_services__service__description', 'client__name',
                     'client__email', 'client__login')
    serializer_class = OrderSerializer
    filter_fields = ('status', 'client_services__service',
                     'client_services__id', 'client__login', 'expired_date',
                     'paid_date', 'created', )


class ServiceViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Service viewset
    """
    queryset = Service.objects.all().select_related(
        'created_by', 'modified_by').prefetch_related('prices')
    search_fields = ('title', 'description', 'id')
    serializer_class = ServiceSerializer
    filter_fields = ('is_enabled', 'is_default', 'period_units', 'type',
                     'created')

    @detail_route(methods=['get'])
    def price(self, request, pk):
        """
        Get price by country or client
        """
        service = self.get_object()
        client = request.GET.get('client', None)
        country = request.GET.get('country', None)
        return Response({
            'status':
            True,
            'price':
            service.get_price(client=client, country=country)
        })


class PriceViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Price viewset
    """
    queryset = Price.objects.all().select_related('created_by', 'modified_by',
                                                  'service', 'country')
    search_fields = ('country__name', 'service__title', 'price', 'id')
    serializer_class = PriceSerializer
    filter_fields = ('is_enabled', 'service', 'country')
