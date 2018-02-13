from rest_framework import serializers

from clients.models import Client

from .models import City, Country, Property, Region, Room


class PropertySerializer(serializers.HyperlinkedModelSerializer):
    """
    Property serializer
    """
    city = serializers.PrimaryKeyRelatedField(
        many=False,
        read_only=False,
        queryset=City.objects.all(),
        allow_null=True,
        required=False,
    )
    created_by = serializers.StringRelatedField(many=False, read_only=True)
    modified_by = serializers.StringRelatedField(many=False, read_only=True)
    client = serializers.SlugRelatedField(
        many=False,
        read_only=False,
        slug_field='login',
        queryset=Client.objects.all())
    rooms = serializers.HyperlinkedRelatedField(
        many=True, read_only=True, view_name='room-detail')

    class Meta:
        model = Property
        fields = ('id', 'name', 'type', 'city', 'address', 'url', 'client',
                  'rooms', 'created', 'modified', 'created_by', 'modified_by')


class RoomSerializer(serializers.HyperlinkedModelSerializer):
    """
    Room serializer
    """
    created_by = serializers.StringRelatedField(many=False, read_only=True)
    modified_by = serializers.StringRelatedField(many=False, read_only=True)
    property = serializers.PrimaryKeyRelatedField(
        many=False,
        read_only=False,
        queryset=Property.objects.all(),
    )

    class Meta:
        model = Room
        fields = ('id', 'name', 'rooms', 'description', 'property', 'created',
                  'modified', 'created_by', 'modified_by')


class CountrySerializer(serializers.HyperlinkedModelSerializer):
    """
    Country serializer
    """

    class Meta:
        model = Country
        fields = ('id', 'name', 'code2', 'code3', 'continent', 'tld', 'phone',
                  'alternate_names', 'is_enabled', 'is_checked')
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
        fields = ('id', 'name', 'alternate_names', 'country', 'is_enabled',
                  'is_checked')


class CitySerializer(serializers.HyperlinkedModelSerializer):
    """
    City serializer
    """
    country = serializers.SlugRelatedField(
        many=False,
        read_only=False,
        slug_field='tld',
        queryset=Country.objects.all())

    region = serializers.PrimaryKeyRelatedField(
        many=False, read_only=False, queryset=Region.objects.all())
    request_client = serializers.SlugRelatedField(
        many=False,
        read_only=False,
        slug_field='login',
        queryset=Client.objects.all())

    class Meta:
        model = City
        fields = ('id', 'name', 'full_name', 'alternate_names', 'latitude',
                  'longitude', 'population', 'region', 'country', 'is_enabled',
                  'is_checked', 'request_client')
