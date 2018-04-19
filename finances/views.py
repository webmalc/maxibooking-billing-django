import logging

from django.http import HttpResponseNotFound
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets
from rest_framework.decorators import list_route
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .filters import OrderFilterSet
from .lib.calc import Calc
from .lib.calc import Exception as CalcException
from .models import Order, Price, Service, ServiceCategory, Transaction
from .serializers import (CalcQuerySerializer, OrderSerializer,
                          PaymentSystemSerializer, PriceSerializer,
                          ServiceCategorySerializer, ServiceSerializer,
                          TransactionSerializer)
from .systems import manager


class PaymentSystemViewSet(viewsets.ViewSet):
    """
    PaymentSystem viewset
    """
    serializer_class = PaymentSystemSerializer
    permission_classes = (IsAuthenticated, )

    def list(self, request):
        entries = manager.systems_list(
            request.query_params.get('order', None), request=request)
        serializer = PaymentSystemSerializer(
            instance=entries.values(), many=True)

        return Response(serializer.data)

    def retrieve(self, request, pk):
        entry = manager.get(
            pk, request.query_params.get('order', None), request=request)
        if not entry:
            return Response(status=404)
        serializer = PaymentSystemSerializer(instance=entry, many=False)

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


class ServiceCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Service viewset
    """
    queryset = ServiceCategory.objects.all().select_related(
        'created_by', 'modified_by').prefetch_related('services')
    search_fields = ('title', 'description', 'id')
    serializer_class = ServiceCategorySerializer


class ServiceViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Service viewset
    """
    queryset = Service.objects.all().select_related(
        'created_by', 'modified_by', 'category').prefetch_related('prices')
    search_fields = ('title', 'description', 'id')
    serializer_class = ServiceSerializer
    filter_fields = ('is_enabled', 'is_default', 'period_units', 'type',
                     'created')

    @list_route(methods=['get'])
    @method_decorator(cache_page(60 * 60 * 24))
    def calc(self, request):
        """
        Calc serivice price
        quantity - client service quantity
        period - service period
        period_units - month, year, day
        country - user country
        """
        query = CalcQuerySerializer(data=request.GET)

        if not query.is_valid():
            return Response({'errors': query.errors, 'status': False})

        data = query.data
        period = data.get('period')
        prices = []

        if period:
            service = Service.objects.get_by_period(
                service_type='rooms',
                period=data.get('period'),
                period_units=data.get('period_units'),
            )
            if not service:
                return Response({
                    'errors': {
                        'service': ['service not found.']
                    },
                    'status': False
                })
            services = [service]
        else:
            services = Service.objects.get_all_periods(
                service_type='rooms',
                period_units=data.get('period_units'),
            )

        for service in services:
            try:
                price = Calc.factory(service).calc(
                    quantity=data.get('quantity'), country=data.get('country'))
                prices.append({
                    'status': True,
                    'price': price.amount,
                    'price_currency': price.currency.code,
                    'period': service.period
                })
            except CalcException as e:
                return Response({
                    'errors': {
                        'calc': [str(e)]
                    },
                    'status': False
                })

        prices_count = len(prices)
        if not prices_count:
            return Response({
                'errors': {
                    'calc': 'Empty prices'
                },
                'status': False
            })

        response = prices[0] if prices_count == 1 else prices
        return Response(response)


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

    system = manager.get(system_id, request=request)
    if not system or not hasattr(system, 'response'):
        return HttpResponseNotFound('Payment system not found.')
    return system.response(request)
