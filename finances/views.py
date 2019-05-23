import logging

from django.http import HttpResponseNotFound
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets
from rest_framework.decorators import list_route
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .filters import OrderFilterSet
from .lib.calc import CalcByQuery, CalcException
from .models import Order, Price, Service, ServiceCategory, Transaction
from .serializers import (CalcQuerySerializer, OrderSerializer,
                          PaymentSystemListSerializer, PaymentSystemSerializer,
                          PriceSerializer, ServiceCategorySerializer,
                          ServiceSerializer, TransactionSerializer)
from .systems import manager


class PaymentSystemViewSet(viewsets.ViewSet):
    """
    PaymentSystem viewset
    """
    serializer_class = PaymentSystemSerializer
    permission_classes = (IsAuthenticated, )

    def list(self, request):
        entries = manager.systems_list(request.query_params.get('order', None),
                                       request=request)
        serializer = PaymentSystemListSerializer(instance=entries.values(),
                                                 many=True)

        return Response(serializer.data)

    def retrieve(self, request, pk):
        entry = manager.get(pk,
                            request.query_params.get('order', None),
                            request=request)
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

    @list_route(methods=['get'], permission_classes=[IsAuthenticated])
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

        calc = CalcByQuery(query.data)
        try:
            prices = calc.get_prices()
            response = prices[0] if len(prices) == 1 else {
                'status': True,
                'prices': prices
            }
        except CalcException as exception:
            response = {'errors': {'calc': [str(exception)]}, 'status': False}

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
@xframe_options_exempt
def payment_system_response(request, system_id, action='response'):
    """
    Payment system check order response view.
    """
    logger = logging.getLogger('billing')
    logger.info(
        'Payment system response; System_id: {}; BODY: {}; GET: {}; POST: {}'.
        format(
            system_id,
            request.body.decode('utf-8'),
            dict(request.GET),
            dict(request.POST),
        ))

    system = manager.get(system_id, request=request)
    if not system or not hasattr(system, action):
        return HttpResponseNotFound('Payment system not found.')
    method = getattr(system, action)
    response = method(request)

    return response
