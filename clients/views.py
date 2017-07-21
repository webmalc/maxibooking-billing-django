import json

from django.utils.translation import ugettext_lazy as _
from rest_framework import viewsets
from rest_framework.decorators import detail_route
from rest_framework.response import Response

from .models import Client
from .serializers import ClientSerializer
from .tasks import install_client_task, mail_client_task


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

    @detail_route(methods=['post'])
    def install(self, request, login=None):
        """
        Install user
        """
        client = self.get_object()
        if client.installation == 'installed':
            return Response({
                'status': False,
                'message': 'client already installed'
            })

        install_client_task.delay(client_id=client.id)
        return Response({
            'status': True,
            'message': 'client installation begin'
        })

    @detail_route(methods=['post'])
    def install_result(self, request, login=None):
        """
        Receive installation status
        """
        client = self.get_object()
        request_json = json.loads(request.body)

        if client.installation == 'installed':
            return Response({
                'status': False,
                'message': 'client already installed'
            })

        if all(k in request_json for k in ('status', 'url', 'password')):
            if request_json['status']:
                client.installation = 'installed'
                client.save()
                mail_client_task.delay(
                    subject=_('Registation successefull'),
                    template='emails/registration.html',
                    data={
                        'login': client.login,
                        'url': request_json['url'],
                        'password': request_json['password']
                    },
                    client_id=client.id)
                return Response({'status': True})
            else:
                mail_client_task.delay(
                    subject=_('Registation failed'),
                    template='emails/registration_fail.html',
                    data={},
                    client_id=client.id)

        return Response({'status': False})
