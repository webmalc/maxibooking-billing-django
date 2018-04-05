from ajax_select import register
from django.contrib.auth import get_user_model
from django.db.models import Q

from billing.lookup import BaseLookup

from .models import Client, ClientService


@register('order_client_services')
class ClientServiceLookup(BaseLookup):
    model = ClientService


@register('clients')
class ClientLookup(BaseLookup):
    model = Client


@register('users')
class UserLookup(BaseLookup):
    model = get_user_model()

    def get_query(self, q, request):
        query = Q(username__icontains=q)
        query.add(Q(last_name__icontains=q), Q.OR)
        query.add(Q(email__icontains=q), Q.OR)

        return self.model.objects.filter(query).order_by('username')
