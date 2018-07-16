from django.forms.models import model_to_dict
from rest_framework import serializers

from billing.serializers import NestedUpdateSerializerMixin
from finances.models import Service
from hotels.models import City, Country, Region

from .models import (Client, ClientAuth, ClientRu, ClientService,
                     ClientWebsite, Company, CompanyRu, CompanyWorld)


class CompanyWorldSerializer(serializers.ModelSerializer):
    """
    Company world serializer
    """
    created_by = serializers.StringRelatedField(many=False, read_only=True)
    modified_by = serializers.StringRelatedField(many=False, read_only=True)
    company = serializers.PrimaryKeyRelatedField(
        many=False, read_only=False, queryset=Company.objects.all())

    class Meta:
        model = CompanyWorld
        lookup_field = 'company__pk'
        fields = ('id', 'company', 'swift', 'created', 'modified',
                  'created_by', 'modified_by')


class CompanyRuSerializer(serializers.ModelSerializer):
    """
    Company ru serializer
    """

    class Meta:
        model = CompanyRu
        fields = ('form', 'ogrn', 'inn', 'kpp', 'bik', 'corr_account',
                  'boss_firstname', 'boss_lastname', 'boss_patronymic',
                  'boss_operation_base', 'proxy_number', 'proxy_date')


class ClientAuthSerializer(serializers.ModelSerializer):
    """
    Company serializer
    """
    created_by = serializers.StringRelatedField(many=False, read_only=True)
    modified_by = serializers.StringRelatedField(many=False, read_only=True)
    client = serializers.SlugRelatedField(
        many=False,
        read_only=False,
        slug_field='login',
        queryset=Client.objects.all())

    class Meta:
        model = ClientAuth
        fields = ('id', 'client', 'auth_date', 'ip', 'user_agent', 'created',
                  'modified', 'created_by', 'modified_by')


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
    ru = CompanyRuSerializer(allow_null=True, required=False)
    world = serializers.StringRelatedField(many=False, read_only=True)

    class Meta:
        model = Company
        fields = ('id', 'name', 'client', 'city', 'region', 'address',
                  'postal_code', 'account_number', 'bank', 'created',
                  'modified', 'created_by', 'modified_by', 'world', 'ru')
        references = {
            'ru': 'clients.CompanyRu',
        }
        reference_parent = 'company'


class WebsiteSerializer(serializers.ModelSerializer):
    """
    This class is serializer for the client's website information.
    """
    created_by = serializers.StringRelatedField(many=False, read_only=True)
    modified_by = serializers.StringRelatedField(many=False, read_only=True)
    client = serializers.SlugRelatedField(
        many=False,
        read_only=False,
        slug_field='login',
        queryset=Client.objects.all())

    class Meta:
        model = ClientWebsite
        lookup_field = 'client__login'
        fields = ('id', 'client', 'url', 'is_enabled', 'created', 'modified',
                  'created_by', 'modified_by')


class ClientRuSerializer(serializers.ModelSerializer):
    """
    This class is serializer for the client's passport information.
    """
    created_by = serializers.StringRelatedField(many=False, read_only=True)
    modified_by = serializers.StringRelatedField(many=False, read_only=True)
    client = serializers.SlugRelatedField(
        many=False,
        read_only=False,
        slug_field='login',
        queryset=Client.objects.all())

    class Meta:
        model = ClientRu
        lookup_field = 'client__login'
        fields = ('id', 'client', 'passport_serial', 'passport_number',
                  'passport_date', 'passport_issued_by', 'inn', 'created',
                  'modified', 'created_by', 'modified_by')


class ClientSerializer(NestedUpdateSerializerMixin,
                       serializers.HyperlinkedModelSerializer):
    """
    Client serializer
    """

    properties = serializers.HyperlinkedRelatedField(
        many=True, read_only=True, view_name='property-detail')
    ru = serializers.StringRelatedField(many=False, read_only=True)
    created_by = serializers.StringRelatedField(many=False, read_only=True)
    modified_by = serializers.StringRelatedField(many=False, read_only=True)
    country = serializers.SlugRelatedField(
        many=False,
        read_only=False,
        slug_field='tld',
        queryset=Country.objects.all())
    city = serializers.PrimaryKeyRelatedField(
        many=False,
        read_only=False,
        allow_null=True,
        required=False,
        queryset=City.objects.all())
    region = serializers.PrimaryKeyRelatedField(
        many=False,
        read_only=False,
        allow_null=True,
        required=False,
        queryset=Region.objects.all())
    restrictions = serializers.SerializerMethodField()

    def get_restrictions(self, obj):
        return model_to_dict(obj.restrictions)

    class Meta:
        model = Client
        fields = ('id', 'login', 'email', 'phone', 'name', 'description',
                  'get_status_display', 'status', 'country', 'region', 'city',
                  'address', 'postal_code', 'ru', 'installation',
                  'trial_activated', 'url', 'properties', 'restrictions',
                  'disabled_at', 'ip', 'created', 'modified', 'created_by',
                  'modified_by')
        lookup_field = 'login'
        references = {}
        reference_parent = 'client'


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
            attrs.get('begin'), attrs.get('end'),
            attrs.get('pk') is None)
        ClientService.validate_service(
            attrs.get('service'), attrs.get('client'))
        return attrs

    class Meta:
        model = ClientService
        fields = ('id', 'is_enabled', 'status', 'price', 'price_currency',
                  'country', 'quantity', 'start_at', 'begin', 'end', 'service',
                  'client', 'created', 'modified', 'created_by', 'modified_by')
