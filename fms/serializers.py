from rest_framework import serializers

from .models import Fms, Kpp

_fields = ('id', 'internal_id', 'name', 'code', 'end_date')
_lookup_field = 'internal_id'


class KppSerializer(serializers.HyperlinkedModelSerializer):
    """
    Kpp serializer
    """

    class Meta:
        model = Kpp
        fields = _fields
        lookup_field = _lookup_field


class FmsSerializer(serializers.HyperlinkedModelSerializer):
    """
    Fms serializer
    """

    class Meta:
        model = Fms
        fields = _fields
        lookup_field = _lookup_field
