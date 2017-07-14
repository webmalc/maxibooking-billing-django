from rest_framework import serializers

from .models import City, Country, Region


class CountrySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Country
        fields = ('id', 'name', 'code2', 'code3', 'continent', 'tld', 'phone',
                  'alternate_names')
        lookup_field = 'tld'
