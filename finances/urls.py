"""
The finances urls module
"""
from django.conf.urls import url
from rest_framework.routers import SimpleRouter

from .views import (OrderViewSet, PaymentSystemViewSet, PriceViewSet,
                    RateViewSet, ServiceCategoryViewSet, ServiceViewSet,
                    TransactionViewSet, payment_system_response)

router = SimpleRouter()
router.register(r'services', ServiceViewSet)
router.register(r'service-categories', ServiceCategoryViewSet)
router.register(r'prices', PriceViewSet)
router.register(r'orders', OrderViewSet)
router.register(r'transactions', TransactionViewSet)
router.register(r'rates', RateViewSet)
router.register(
    r'payment-systems', PaymentSystemViewSet, base_name='payment-systems')

urlpatterns = [
    url(
        r'^payment-system/response/(?P<system_id>[a-zA-z0-9\-_]+)/'
        '(?P<action>[a-z]+)',
        payment_system_response,
        name='payment-system-response-action'),
    url(r'^payment-system/response/(?P<system_id>[a-zA-z0-9\-_]+)',
        payment_system_response,
        name='payment-system-response')
]
