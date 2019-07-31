"""
Command for sending messages
"""
from django.conf import settings
from django.core.management.base import BaseCommand

from billing.lib.messengers.mailer import mail_client, mail_managers


class Command(BaseCommand):
    """
    Send a test email to the admins
    """

    def add_arguments(self, parser):
        """
        Parse the command arguments
        """
        parser.add_argument(
            'type',
            nargs='?',
            default='managers',
            choices=['managers', 'clients'])

        parser.add_argument(
            'locale', nargs='?', default='en', choices=['en', 'ru'])

        parser.add_argument(
            'template',
            nargs='?',
            default='registration',
            choices=['registration', 'registration_fail'],
        )

    @staticmethod
    def _clients(locale='ru', template='registration'):
        """
        Send emails to the clients
        """
        for manager in settings.MANAGERS:
            mail_client(
                subject='Test client message',
                template='emails/{}.html'.format(template),
                data={
                    'login': 'username',
                    'name': 'John Doe',
                    'url': '/user/login',
                    'website': 'website',
                    'password': 'password'
                },
                email=manager[1],
                lang=locale)

    @staticmethod
    def _managers():
        """
        Send emails to the managers
        """
        mail_managers(
            'Test manager message',
            data={
                'text':
                '<p>Lorem ipsum dolor sit amet, consectetur adipiscing elit.\
Morbi a imperdiet massa. Praesent enim neque, cursus placerat ultrices quis,\
porttitor vitae nisi. Interdum et malesuada fames ac ante\
ipsum primis in faucibus.</p><p>\
Morbi a imperdiet massa. Praesent enim neque, cursus placerat ultrices quis,\
ipsum primis in faucibus.</p>'
            })

    def handle(self, *args, **options):
        """
        Send emails
        """
        getattr(self, '_' + options['type'])(
            options['locale'],
            options['template'],
        )
        self.stdout.write(self.style.SUCCESS('Emails have been sent'))
