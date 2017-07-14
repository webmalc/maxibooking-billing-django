from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser

from .models import Country
from .serializers import CountrySerializer


class CountryViewSet(viewsets.ModelViewSet):
    """
    Country viewset
    """
    queryset = Country.objects.all()
    serializer_class = CountrySerializer
    lookup_field = 'tld'
