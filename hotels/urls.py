from django.conf.urls import include, url
from rest_framework.routers import SimpleRouter

from .views import CityViewSet, CountryViewSet, RegionViewSet

router = SimpleRouter()
router.register(r'countries', CountryViewSet)
router.register(r'regions', RegionViewSet)
router.register(r'cities', CityViewSet)

urlpatterns = [url(r'^', include(router.urls))]
