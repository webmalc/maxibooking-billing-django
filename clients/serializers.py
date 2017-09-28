from rest_framework import serializers

from finances.models import Service
from hotels.models import Country

from .models import Client, ClientService


class ClientSerializer(serializers.HyperlinkedModelSerializer):
    """
    Client serializer
    """

    properties = serializers.HyperlinkedRelatedField(
        many=True, read_only=True, view_name='property-detail')
    created_by = serializers.StringRelatedField(many=False, read_only=True)
    modified_by = serializers.StringRelatedField(many=False, read_only=True)
    country = serializers.SlugRelatedField(
        many=False,
        read_only=False,
        slug_field='tld',
        queryset=Country.objects.all())

    class Meta:
        model = Client
        fields = ('id', 'login', 'email', 'phone', 'name', 'description',
                  'get_status_display', 'status', 'country', 'installation',
                  'properties', 'rooms_limit', 'disabled_at', 'created',
                  'modified', 'created_by', 'modified_by')
        lookup_field = 'login'


class ClientServiceSerializer(serializers.HyperlinkedModelSerializer):
    """
    ClientService serializer
    """

    client = serializers.SlugRelatedField(
        many=False,
        read_only=False,
        slug_field='login',
        queryset=Client.objects.all())
    service = serializers.PrimaryKeyRelatedField(
        many=False, read_only=False, queryset=Service.objects.all())
    created_by = serializers.StringRelatedField(many=False, read_only=True)
    modified_by = serializers.StringRelatedField(many=False, read_only=True)
    country = serializers.SlugRelatedField(
        many=False, read_only=True, slug_field='tld')

    def validate(self, attrs):
        ClientService.validate_dates(attrs.get('begin'), attrs.get('end'))
        ClientService.validate_service(
            attrs.get('service'), attrs.get('client'))
        return attrs

    class Meta:
        model = ClientService
        fields = ('id', 'is_enabled', 'status', 'price', 'price_currency',
                  'country', 'quantity', 'start_at', 'begin', 'end', 'service',
                  'client', 'created', 'modified', 'created_by', 'modified_by')
