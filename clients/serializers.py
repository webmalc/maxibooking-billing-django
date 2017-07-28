from rest_framework import serializers

from finances.models import Service

from .models import Client, ClientService


class ClientSerializer(serializers.HyperlinkedModelSerializer):
    """
    Client serializer
    """

    properties = serializers.HyperlinkedRelatedField(
        many=True, read_only=True, view_name='property-detail')
    created_by = serializers.StringRelatedField(many=False, read_only=True)
    modified_by = serializers.StringRelatedField(many=False, read_only=True)

    class Meta:
        model = Client
        fields = ('id', 'login', 'email', 'phone', 'name', 'description',
                  'get_status_display', 'status', 'properties', 'installation',
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
    service = serializers.HyperlinkedRelatedField(
        many=False,
        read_only=False,
        view_name='service-detail',
        queryset=Service.objects.all())
    created_by = serializers.StringRelatedField(many=False, read_only=True)
    modified_by = serializers.StringRelatedField(many=False, read_only=True)

    class Meta:
        model = ClientService
        fields = ('id', 'is_enabled', 'price', 'quantity', 'start_at', 'begin',
                  'end', 'service', 'client', 'created', 'modified',
                  'created_by', 'modified_by')
