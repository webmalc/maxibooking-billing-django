from django.conf.urls import include, url
from rest_framework.routers import SimpleRouter

from .views import OrderViewSet, PriceViewSet, ServiceViewSet

router = SimpleRouter()
router.register(r'services', ServiceViewSet)
router.register(r'prices', PriceViewSet)
router.register(r'orders', OrderViewSet)

urlpatterns = [url(r'^', include(router.urls))]
