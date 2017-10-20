from django.conf.urls import include, url
from rest_framework.routers import SimpleRouter

from .views import FmsViewSet, KppViewSet

router = SimpleRouter()
router.register(r'fms-kpp', KppViewSet)
router.register(r'fms-fms', FmsViewSet)

urlpatterns = [url(r'^', include(router.urls))]
