from rest_framework import serializers

from clients.models import Client

from .models import City, Country, Property, Region


class PropertySerializer(serializers.HyperlinkedModelSerializer):
    """
    Property serializer
    """
    city = serializers.PrimaryKeyRelatedField(
        many=False, read_only=False, queryset=City.objects.all())
    created_by = serializers.StringRelatedField(many=False, read_only=True)
    modified_by = serializers.StringRelatedField(many=False, read_only=True)
    client = serializers.SlugRelatedField(
        many=False,
        read_only=False,
        slug_field='login',
        queryset=Client.objects.all())

    class Meta:
        model = Property
        fields = ('id', 'name', 'type', 'city', 'address', 'url', 'rooms',
                  'client', 'created', 'modified', 'created_by', 'modified_by')


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
        many=False,
        read_only=False,
        slug_field='tld',
        queryset=Country.objects.all())

    class Meta:
        model = Region
        fields = ('id', 'name', 'alternate_names', 'country')


class CitySerializer(serializers.HyperlinkedModelSerializer):
    """
    City serializer
    """
    country = serializers.SlugRelatedField(
        many=False,
        read_only=False,
        slug_field='tld',
        queryset=Country.objects.all())

    region = serializers.SlugRelatedField(
        many=False,
        read_only=False,
        slug_field='display_name',
        queryset=Region.objects.all())

    class Meta:
        model = City
        fields = ('id', 'name', 'display_name', 'alternate_names', 'latitude',
                  'longitude', 'population', 'region', 'country')
