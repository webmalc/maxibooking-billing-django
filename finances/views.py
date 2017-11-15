import logging

from django.http import HttpResponseNotFound
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets
from rest_framework.decorators import detail_route
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .filters import OrderFilterSet
from .models import Order, Price, Service, Transaction
from .serializers import (OrderSerializer, PaymentSystemDisplaySerializer,
                          PaymentSystemSerializer, PriceSerializer,
                          ServiceSerializer, TransactionSerializer)
from .systems import manager


class PaymentSystemViewSet(viewsets.ViewSet):
    """
    PaymentSystem viewset
    """
    serializer_class = PaymentSystemSerializer
    permission_classes = (IsAuthenticated, )

    def list(self, request):
        entries = manager.list(
            request.query_params.get('order', None), request=request)
        serializer = PaymentSystemSerializer(
            instance=entries.values(), many=True)

        return Response(serializer.data)

    def retrieve(self, request, pk):
        entry = manager.get(
            pk, request.query_params.get('order', None), request=request)
        if not entry:
            return Response(status=404)
        serializer = PaymentSystemDisplaySerializer(instance=entry, many=False)

        return Response(serializer.data)


class TransactionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Order viewset
    """
    queryset = Transaction.objects.all().select_related(
        'created_by', 'modified_by', 'order')
    search_fields = ('=pk', '=order__pk', 'order__client__name',
                     'order__client__email', 'order__client__login')
    serializer_class = TransactionSerializer
    filter_fields = ('order', 'created')


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
    filter_class = OrderFilterSet
    serializer_class = OrderSerializer


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
        price = service.get_price(client=client, country=country)
        return Response({
            'status':
            True,
            'price':
            getattr(price, 'amount', None),
            'price_currency':
            getattr(getattr(price, 'currency', None), 'code', None)
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


@csrf_exempt
def payment_system_response(request, system_id):
    """
    Payment system check order response view.
    """
    logger = logging.getLogger('billing')
    logger.info(
        'Payment system response; System_id: {}; GET: {}; POST: {}'.format(
            system_id, dict(request.GET), dict(request.POST)))

    system = manager.get(system_id)
    if not system or not hasattr(system, 'response'):
        return HttpResponseNotFound('Payment system not found.')
    return system.response(request)
