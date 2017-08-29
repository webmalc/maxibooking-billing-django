from rest_framework import viewsets

from .models import City, Country, Property, Region
from .serializers import (CitySerializer, CountrySerializer,
                          PropertySerializer, RegionSerializer)


class PropertyViewSet(viewsets.ModelViewSet):
    """
    Property viewset
    """
    queryset = Property.objects.all().select_related('city', 'created_by',
                                                     'modified_by')
    search_fields = ('name', 'city__name', 'city__alternate_names',
                     'description')
    serializer_class = PropertySerializer


class CountryViewSet(viewsets.ModelViewSet):
    """
    Country viewset
    """
    queryset = Country.objects.all()
    serializer_class = CountrySerializer
    filter_fields = ('name', 'code2', 'code3', 'continent')
    search_fields = ('name', 'alternate_names', 'code2', 'code3')
    lookup_field = 'tld'
    page_size_query_param = 'page_size'
    max_page_size = 1000


class RegionViewSet(viewsets.ModelViewSet):
    """
    Region viewset
    """
    queryset = Region.objects.all().select_related('country')
    filter_fields = ('country', )
    search_fields = ('name', 'alternate_names', 'country__name',
                     'country__alternate_names')
    serializer_class = RegionSerializer


class CityViewSet(viewsets.ModelViewSet):
    """
    City viewset
    """
    queryset = City.objects.all().select_related('country', 'region')
    filter_fields = ('country', 'region')
    search_fields = ('name', 'alternate_names')
    serializer_class = CitySerializer
