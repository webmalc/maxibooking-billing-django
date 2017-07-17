from rest_framework import viewsets

from .models import City, Country, Region
from .serializers import CitySerializer, CountrySerializer, RegionSerializer


class CountryViewSet(viewsets.ModelViewSet):
    """
    Country viewset
    """
    queryset = Country.objects.all()
    serializer_class = CountrySerializer
    lookup_field = 'tld'


class RegionViewSet(viewsets.ModelViewSet):
    """
    Region viewset
    """
    queryset = Region.objects.all().select_related('country')
    serializer_class = RegionSerializer


class CityViewSet(viewsets.ModelViewSet):
    """
    City viewset
    """
    queryset = City.objects.all().select_related('country', 'region')
    serializer_class = CitySerializer
