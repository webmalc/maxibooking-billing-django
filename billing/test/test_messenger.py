"""
Test suite for the messenger
"""
import pytest

from billing.lib.messengers import mailer
from clients.models import Client

pytestmark = pytest.mark.django_db  # pylint: invalid-name


def test_mail_managers(mailoutbox):
    """
    Should send an email to the system managers
    """
    mailer.mail_managers(subject='Text message', data={'text': 'Test text'})
    assert len(mailoutbox) == 1
    mail = mailoutbox[0]
    assert mail.recipients() == ['admin@example.com', 'manager@example.com']
    assert 'Text message' in mail.subject
    assert 'Test text' in mail.alternatives[0][0]


def test_mail_client_by_email(mailoutbox):
    """
    Should send an email by a client email
    """
    mailer.mail_client(subject='Text message',
                       template='emails/registration_fail.html',
                       data={},
                       email='client@example.com')

    assert len(mailoutbox) == 1
    mail = mailoutbox[0]
    assert mail.recipients() == ['client@example.com']
    assert 'Text message' in mail.subject
    assert 'Registation failure' in mail.alternatives[0][0]


def test_mail_client_by_client(mailoutbox, settings):
    """
    Should send an email by a client object
    """

    def send(login):
        client = Client.objects.get(login=login)
        mailer.mail_client(subject='Registation failure',
                           template='emails/registration_fail.html',
                           data={},
                           client=client)

    send('user-one')
    assert len(mailoutbox) == 1
    mail = mailoutbox[0]
    assert mail.recipients() == ['user@one.com']
    assert 'User One, Registation failure' in mail.subject
    assert 'Registation failure' in mail.alternatives[0][0]

    send('user-rus')
    assert len(mailoutbox) == 2
    mail = mailoutbox[1]
    assert mail.recipients() == ['user@rus.com']
    assert 'Ошибка при регистрации' in mail.subject
    assert 'Ошибка при регистрации' in mail.alternatives[0][0]

    settings.MB_COUNTRIES_OVERWRITE = {'us': 'ru'}
    send('user-one')
    assert len(mailoutbox) == 3
    mail = mailoutbox[2]
    assert mail.recipients() == ['user@one.com']
    assert 'Ошибка при регистрации' in mail.subject
    assert 'Ошибка при регистрации' in mail.alternatives[0][0]


def test_mail_client_by_client_subject_format(mailoutbox, settings):
    """
    Should format the mail subject with a client name
    """
    settings.EMAIL_SUBJECT_PREFIX = 'Prefix: '
    client = Client.objects.get(login='user-one')
    subject = 'test subject'

    mailer.mail_client(subject=subject,
                       template='emails/registration_fail.html',
                       data={},
                       client=client)

    mail = mailoutbox[0]
    assert mail.subject == 'Prefix: User One, test subject'

    Client.objects.filter(login='user-one').update(name=None)
    client = Client.objects.get(login='user-one')

    mailer.mail_client(subject=subject,
                       template='emails/registration_fail.html',
                       data={},
                       client=client)
    mail = mailoutbox[1]
    assert mail.subject == 'Prefix: test subject'
