import logging

from billing.exceptions import BaseException
from billing.lib import mb
from billing.lib.lang import select_locale
from django.utils.translation import ugettext_lazy as _
from rest_framework import viewsets
from rest_framework.decorators import detail_route
from rest_framework.response import Response

from .models import (Client, ClientAuth, ClientRu, ClientService,
                     ClientWebsite, Company, CompanyRu, CompanyWorld)
from .serializers import (ClientAuthSerializer, ClientRuSerializer,
                          ClientSerializer, ClientServiceSerializer,
                          CompanyRuSerializer, CompanySerializer,
                          CompanyWorldSerializer, WebsiteSerializer)
from .tasks import install_client_task, mail_client_task


class ClientAuthViewSet(viewsets.ModelViewSet):
    queryset = ClientAuth.objects.all().select_related(
        'created_by',
        'modified_by',
        'client',
    )
    search_fields = ('=id', 'ip', 'client__name', 'client__email',
                     'client__login', 'user_agent')

    serializer_class = ClientAuthSerializer
    filter_fields = ('client', )


class ClientRuViewSet(viewsets.ModelViewSet):
    queryset = ClientRu.objects.all().select_related(
        'created_by',
        'modified_by',
        'client',
    )
    search_fields = ('=id', 'client__login', 'client__email', 'client__name',
                     'passport_number', 'passport_issued_by',
                     'passport_serial', 'inn')
    filter_fields = ('client', )
    serializer_class = ClientRuSerializer
    lookup_field = 'client__login'


class WebsiteViewSet(viewsets.ModelViewSet):
    queryset = ClientWebsite.objects.all().select_related(
        'created_by',
        'modified_by',
        'client',
    )
    search_fields = ('=id', 'client__login', 'client__email', 'client__name',
                     'url')
    filter_fields = ('client', 'is_enabled')
    serializer_class = WebsiteSerializer
    lookup_field = 'client__login'


class CompanyWorldViewSet(viewsets.ModelViewSet):
    queryset = CompanyWorld.objects.all().select_related(
        'created_by',
        'modified_by',
        'company',
    )
    search_fields = ('=id', 'company__name', 'company__account_number',
                     'swift')
    filter_fields = ('company', )
    serializer_class = CompanyWorldSerializer
    lookup_field = 'company__pk'


class CompanyRuViewSet(viewsets.ModelViewSet):
    queryset = CompanyRu.objects.all().select_related(
        'created_by',
        'modified_by',
        'company',
    )
    search_fields = ('=id', 'company__name', 'company__account_number', 'form',
                     'ogrn', 'inn', 'kpp', 'bik', 'corr_account',
                     'boss_lastname', 'proxy_number')
    filter_fields = ('company', 'form')
    serializer_class = CompanyRuSerializer
    lookup_field = 'company__pk'


class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all().select_related(
        'created_by', 'modified_by', 'client', 'region', 'city', 'ru', 'world')

    search_fields = ('id', 'client__login', 'client__email', 'client__name',
                     'name', 'ru__boss_lastname', 'ru__ogrn', 'ru__inn',
                     'ru__kpp', 'account_number', 'ru__bik', 'world__swift')
    serializer_class = CompanySerializer
    filter_fields = ('client', )


class ClientServiceViewSet(viewsets.ModelViewSet):
    queryset = ClientService.objects.all().select_related(
        'created_by', 'modified_by', 'client', 'service')
    search_fields = ('id', 'service__title', 'client__name', 'client__email',
                     'client__login')
    serializer_class = ClientServiceSerializer
    filter_fields = ('client', 'service', 'is_enabled', 'begin', 'end')


class ClientViewSet(viewsets.ModelViewSet):
    """
    This class contains the client's routes.
    """
    queryset = Client.objects.all().select_related(
        'created_by', 'modified_by', 'country',
        'restrictions', 'ru', 'website').prefetch_related(
            'properties', 'services', 'services__service')
    search_fields = (
        'login',
        'email',
        'description',
        'phone',
        'status',
        'website__url',
    )
    serializer_class = ClientSerializer
    filter_fields = (
        'status',
        'installation',
        'country',
        'email',
        'website__url',
        'website__is_enabled',
    )
    lookup_field = 'login'

    @detail_route(methods=['get'])
    def tariff_detail(self, request, login=None):
        """
        Show client tariff
        """
        client = self.get_object()
        tariff = client.services_by_category()
        next_tariff = client.services_by_category(next=True)
        result = {'main': None, 'next': None}

        def to_dict(group):
            return {
                'rooms': group.quantity,
                'title': group.category.title,
                'price': group.price.amount,
                'currency': str(group.price.currency),
                'begin': group.begin,
                'end': group.end,
                'period': list(group.client_services)[0].service.period,
            }

        if len(tariff):
            result['main'] = to_dict(tariff[0])
        if len(next_tariff):
            result['next'] = to_dict(next_tariff[0])

        return Response(result)

    @detail_route(methods=['post'])
    def tariff_update(self, request, login=None):
        """
        Update client services
        """
        client = self.get_object()
        if client.status != 'active':
            return Response({'status': False, 'message': 'invalid client'})

        request_json = request.data
        logging.getLogger('billing').info(
            'Client services update. Client {}; rooms {}; period: {}'.format(
                client, request_json.get('rooms'), request_json.get('period')))

        if all(k in request_json for k in ('rooms', 'period')):
            try:
                ClientService.objects.client_tariff_update(
                    client, request_json['rooms'], request_json['period'])
                return Response({
                    'status':
                    True,
                    'message':
                    'client services successfully updated'
                })
            except BaseException as e:
                logging.getLogger('billing').error(
                    'Failed client services up. Client: {}. Error: {}'.format(
                        client, e))
                return Response({
                    'status': False,
                    'message': 'failed update. Error: {}'.format(e)
                })
        return Response({'status': False, 'message': 'invalid request'})

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
    def trial(self, request, login=None):
        """
        Activate user trial
        """
        client = self.get_object()
        logging.getLogger('billing').info(
            'Begin client trial installation. Id: {}; login: {}'.format(
                client.id, client.login))
        try:
            ClientService.objects.make_trial(client)
            return Response({
                'status': True,
                'message': 'trial successfully activated'
            })
        except BaseException as e:
            logging.getLogger('billing').error(
                'Failed client trial installation. Id: {}; login: {}'.format(
                    client.id, client.login))
            return Response({
                'status': False,
                'message': 'trial activation failed: {}'.format(e)
            })

    @detail_route(methods=['post'])
    def install(self, request, login=None):
        """
        Install client maxibooking
        """
        client = self.get_object()
        if client.installation == 'installed':
            return Response({
                'status': False,
                'message': 'client already installed'
            })

        logging.getLogger('billing').info(
            'Get client installation request. Id: {}; login: {}'.format(
                client.id, client.login))

        install_client_task.apply_async(
            kwargs={'client_id': client.id}, queue='priority_high')
        return Response({
            'status': True,
            'message': 'client installation begin'
        })

    @detail_route(methods=['post'])
    def fixtures(self, request, login=None):
        """
        Install client fixtures
        """
        client = self.get_object()
        if client.installation == 'not_installed':
            return Response({
                'status': False,
                'message': 'client not installed'
            })
        if client.installation == 'process':
            return Response({
                'status': False,
                'message': 'client installation in process'
            })

        logging.getLogger('billing').info(
            'Get client fixtures request. Id: {}; login: {}'.format(
                client.id, client.login))
        response = mb.client_fixtures(client)
        if response and response.get('status', True):
            return Response({
                'status': True,
                'message': 'client fixtures installed',
                'url': response['url'],
                'token': response['token']
            })
        else:
            return Response({
                'status': False,
                'message': 'client fixtures installation error',
            })

    @detail_route(methods=['post'])
    def install_result(self, request, login=None):
        """
        Receive installation status
        """
        client = self.get_object()
        request_json = request.data

        logging.getLogger('billing').info(
            'Client installation result. Client: {}; status: {}; url: {};'.
            format(client, request_json.get('status'),
                   request_json.get('url')))

        if client.installation == 'installed':
            return Response({
                'status': False,
                'message': 'client already installed'
            })

        if all(k in request_json for k in ('status', 'url', 'password')):
            if request_json['status']:
                client.installation = 'installed'
                client.url = request_json['url']
                client.save()

                with select_locale(client):
                    website = client.website.url if client.website else None
                    mail_client_task.delay(
                        subject='{}, {}'.format(client.name,
                                                _('Welcome to MaxiBooking!')),
                        template='emails/registration.html',
                        data={
                            'login': client.login,
                            'name': client.name,
                            'url': request_json['url'] + '/user/login',
                            'website': website,
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
