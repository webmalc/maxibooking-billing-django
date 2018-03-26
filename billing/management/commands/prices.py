from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand

from clients.models import Client, ClientService
from finances.models import Service
from hotels.models import Room


class Command(BaseCommand):
    """
    Migrate prices
    TODO: DELETE
    """

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting prices migrate'))
        clients = Client.objects.filter(services__service__type='connection')

        self.stdout.write(
            self.style.SUCCESS('Client total: {}'.format(clients.count())))

        for client in clients:
            rooms = Room.objects.count_rooms(client)
            self.stdout.write(
                self.style.SUCCESS('Process client: {}. Rooms: {}'.format(
                    client, rooms)))
            conn = client.services.filter(service__type='connection').first()
            if not conn:
                self.stdout.write(self.style.ERROR('connection not found'))
                continue

            begin = conn.begin
            end = conn.end
            period = conn.service.period
            service = Service.objects.get(
                type='rooms',
                is_enabled=True,
                period=period,
                period_units='month')
            if not service:
                self.stdout.write(
                    self.style.ERROR(
                        'service not found. Period: '.format(period)))
                continue

            client.services.all().delete()
            client_service = ClientService()
            client_service.service = service
            client_service.client = client
            client_service.quantity = rooms
            client_service.status = 'active'
            client_service.begin = begin
            client_service.end = end
            try:
                client_service.full_clean()
                client_service.save()
            except ValidationError as e:
                self.stdout.write(
                    self.style.ERROR(
                        'Cant save client_service. e: '.format(e)))
