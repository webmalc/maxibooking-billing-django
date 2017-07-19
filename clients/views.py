from rest_framework import viewsets
from rest_framework.decorators import detail_route
from rest_framework.response import Response

from .models import Client
from .serializers import ClientSerializer


class ClientViewSet(viewsets.ModelViewSet):
    """
    Client viewset
    """
    queryset = Client.objects.all().select_related(
        'created_by', 'modified_by').prefetch_related('properties')
    search_fields = ('login', 'email', 'description', 'phone', 'status')
    serializer_class = ClientSerializer
    filter_fields = ('status', )
    lookup_field = 'login'

    @detail_route(methods=['post'])
    def confirm(self, request, login=None):
        """
        Change user status to active
        """
        client = self.get_object()
        if client.status != 'not_confirmed':
            return Response({
                'status': False,
                'message': 'client already confirmed'
            })

        client.status = 'active'
        client.save()

        return Response({
            'status': True,
            'message': 'client successfully confirmed'
        })
