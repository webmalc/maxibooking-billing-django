from django.conf.urls import include, url
from rest_framework.routers import SimpleRouter

from .views import (CityViewSet, CountryViewSet, PropertyViewSet,
                    RegionViewSet, RoomViewSet)

router = SimpleRouter()
router.register(r'countries', CountryViewSet)
router.register(r'regions', RegionViewSet)
router.register(r'cities', CityViewSet)
router.register(r'properties', PropertyViewSet)
router.register(r'rooms', RoomViewSet)

urlpatterns = [url(r'^', include(router.urls))]
