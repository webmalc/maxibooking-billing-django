from billing.lib.messengers import mailer
from clients.models import Client


def test_mail_managers(admin_client, mailoutbox):
    mailer.mail_managers(subject='Text message', data={'text': 'Test text'})
    assert len(mailoutbox) == 1
    mail = mailoutbox[0]
    assert mail.recipients() == ['admin@example.com', 'manager@example.com']
    assert 'Text message' in mail.subject
    assert 'Test text' in mail.alternatives[0][0]


def test_mail_client_by_email(admin_client, mailoutbox):
    mailer.mail_client(
        subject='Text message',
        template='emails/registration_fail.html',
        data={},
        email='client@example.com')

    assert len(mailoutbox) == 1
    mail = mailoutbox[0]
    assert mail.recipients() == ['client@example.com']
    assert 'Text message' in mail.subject
    assert 'Registation failed' in mail.alternatives[0][0]


def test_mail_client_by_client(admin_client, mailoutbox):
    def send(login):
        client = Client.objects.get(login=login)
        mailer.mail_client(
            subject='Text message',
            template='emails/registration_fail.html',
            data={},
            client=client)

    send('user-one')
    assert len(mailoutbox) == 1
    mail = mailoutbox[0]
    assert mail.recipients() == ['user@one.com']
    assert 'Text message' in mail.subject
    assert 'Registation failed' in mail.alternatives[0][0]

    send('user-rus')
