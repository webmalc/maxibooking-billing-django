from django.conf.urls import include, url
from rest_framework.routers import SimpleRouter

from .views import (ClientAuthViewSet, ClientServiceViewSet, ClientViewSet,
                    CompanyViewSet, WebsiteViewSet, ClientRuViewSet)

router = SimpleRouter()
router.register(r'clients', ClientViewSet)
router.register(r'companies', CompanyViewSet)
router.register(r'authentications', ClientAuthViewSet)
router.register(r'client-services', ClientServiceViewSet)
router.register(r'client-websites', WebsiteViewSet)
router.register(r'client-payer', ClientRuViewSet)

urlpatterns = [url(r'^', include(router.urls))]
