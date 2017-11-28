from django.forms.models import model_to_dict
from rest_framework import serializers

from billing.serializers import NestedUpdateSerializerMixin
from finances.models import Service
from hotels.models import City, Country, Region

from .models import Client, ClientService, Company, CompanyRu, CompanyWorld


class CompanyWorldSerializer(serializers.ModelSerializer):
    """
    Company world serializer
    """

    class Meta:
        model = CompanyWorld
        fields = ('swift', )


class CompanyRuSerializer(serializers.ModelSerializer):
    """
    Company ru serializer
    """

    class Meta:
        model = CompanyRu
        fields = ('form', 'ogrn', 'inn', 'kpp', 'bik', 'corr_account',
                  'boss_firstname', 'boss_lastname', 'boss_patronymic',
                  'boss_operation_base', 'proxy_number', 'proxy_date')


class CompanySerializer(NestedUpdateSerializerMixin,
                        serializers.ModelSerializer):
    """
    Company serializer
    """
    created_by = serializers.StringRelatedField(many=False, read_only=True)
    modified_by = serializers.StringRelatedField(many=False, read_only=True)
    city = serializers.PrimaryKeyRelatedField(
        many=False, read_only=False, queryset=City.objects.all())
    region = serializers.PrimaryKeyRelatedField(
        many=False, read_only=False, queryset=Region.objects.all())
    client = serializers.SlugRelatedField(
        many=False,
        read_only=False,
        slug_field='login',
        queryset=Client.objects.all())

    world = CompanyWorldSerializer()
    ru = CompanyRuSerializer()

    class Meta:
        model = Company
        fields = ('id', 'name', 'client', 'city', 'region', 'address',
                  'postal_code', 'account_number', 'bank', 'created',
                  'modified', 'created_by', 'modified_by', 'world', 'ru')
        references = {
            'ru': 'clients.CompanyRu',
            'world': 'clients.CompanyWorld'
        }


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
    restrictions = serializers.SerializerMethodField()

    def get_restrictions(self, obj):
        return model_to_dict(obj.restrictions)

    class Meta:
        model = Client
        fields = ('id', 'login', 'email', 'phone', 'name', 'description',
                  'get_status_display', 'status', 'country', 'installation',
                  'url', 'properties', 'restrictions', 'disabled_at', 'ip',
                  'created', 'modified', 'created_by', 'modified_by')
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
        ClientService.validate_dates(
            attrs.get('begin'), attrs.get('end'), attrs.get('pk') is None)
        ClientService.validate_service(
            attrs.get('service'), attrs.get('client'))
        return attrs

    class Meta:
        model = ClientService
        fields = ('id', 'is_enabled', 'status', 'price', 'price_currency',
                  'country', 'quantity', 'start_at', 'begin', 'end', 'service',
                  'client', 'created', 'modified', 'created_by', 'modified_by')
