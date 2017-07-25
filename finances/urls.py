from django.conf.urls import include, url
from rest_framework.routers import SimpleRouter

from .views import ServiceViewSet

router = SimpleRouter()
router.register(r'services', ServiceViewSet)

urlpatterns = [url(r'^', include(router.urls))]
