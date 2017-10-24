from django.conf.urls import include, url
from rest_framework.routers import SimpleRouter

from .views import (OrderViewSet, PaymentSystemViewSet, PriceViewSet,
                    ServiceViewSet)

router = SimpleRouter()
router.register(r'services', ServiceViewSet)
router.register(r'prices', PriceViewSet)
router.register(r'orders', OrderViewSet)
router.register(
    r'payment-systems', PaymentSystemViewSet, base_name='payment-systems')

urlpatterns = [url(r'^', include(router.urls))]
