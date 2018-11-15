from django.db.models import Q
from django_filters import rest_framework as filters

from .models import Country


class CountryFilter(filters.FilterSet):
    with_tld = filters.BooleanFilter(label='with tld', method='filter_tld')

    def filter_tld(self, queryset, name, value):
        if value:
            return queryset.filter(tld__isnull=False).exclude(tld__exact='')
        else:
            return queryset.filter(Q(tld__isnull=True) | Q(tld__exact=''))

    class Meta:
        model = Country
        fields = ('name', 'code2', 'code3', 'continent', 'is_former',
                  'with_tld')
