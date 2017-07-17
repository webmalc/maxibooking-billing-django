from rest_framework import serializers

from .models import City, Country, Region


class CountrySerializer(serializers.HyperlinkedModelSerializer):
    """
    Country serializer
    """

    class Meta:
        model = Country
        fields = ('id', 'name', 'code2', 'code3', 'continent', 'tld', 'phone',
                  'alternate_names')
        lookup_field = 'tld'


class RegionSerializer(serializers.HyperlinkedModelSerializer):
    """
    Region serializer
    """
    country = serializers.SlugRelatedField(
        many=False, read_only=True, slug_field='tld')

    class Meta:
        model = Region
        fields = ('id', 'name', 'alternate_names', 'country')


class CitySerializer(serializers.HyperlinkedModelSerializer):
    """
    City serializer
    """
    country = serializers.SlugRelatedField(
        many=False, read_only=True, slug_field='tld')

    region = serializers.StringRelatedField(many=False, read_only=True)

    class Meta:
        model = City
        fields = ('id', 'name', 'alternate_names', 'latitude', 'longitude',
                  'population', 'region', 'country')
