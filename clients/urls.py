from django.conf.urls import include, url
from rest_framework.routers import SimpleRouter

from .views import ClientServiceViewSet, ClientViewSet

router = SimpleRouter()
router.register(r'clients', ClientViewSet)
router.register(r'client-services', ClientServiceViewSet)

urlpatterns = [url(r'^', include(router.urls))]
