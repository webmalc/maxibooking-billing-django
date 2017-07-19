from django.conf.urls import include, url
from rest_framework.routers import SimpleRouter

from .views import ClientViewSet

router = SimpleRouter()
router.register(r'clients', ClientViewSet)

urlpatterns = [url(r'^', include(router.urls))]
