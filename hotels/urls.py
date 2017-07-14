from django.conf.urls import include, url
from rest_framework.routers import SimpleRouter

from hotels.views import CountryViewSet

router = SimpleRouter()
router.register(r'countries', CountryViewSet)

urlpatterns = [url(r'^', include(router.urls))]
