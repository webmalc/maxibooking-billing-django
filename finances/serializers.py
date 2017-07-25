from rest_framework import serializers

from .models import Service


class ServiceSerializer(serializers.HyperlinkedModelSerializer):
    """
    Service serializer
    """

    created_by = serializers.StringRelatedField(many=False, read_only=True)
    modified_by = serializers.StringRelatedField(many=False, read_only=True)

    class Meta:
        model = Service
        fields = ('id', 'title', 'description', 'price', 'period',
                  'period_units', 'period_days', 'is_enabled', 'created',
                  'modified', 'created_by', 'modified_by')
