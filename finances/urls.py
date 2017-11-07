from django.conf.urls import url
from rest_framework.routers import SimpleRouter

from .views import (OrderViewSet, PaymentSystemViewSet, PriceViewSet,
                    ServiceViewSet, payment_system_response)

router = SimpleRouter()
router.register(r'services', ServiceViewSet)
router.register(r'prices', PriceViewSet)
router.register(r'orders', OrderViewSet)
router.register(
    r'payment-systems', PaymentSystemViewSet, base_name='payment-systems')

urlpatterns = [
    url(r'^payment-system/response/(?P<system_id>[a-zA-z0-9\-_]+)',
        payment_system_response,
        name='payment-system-response')
]
