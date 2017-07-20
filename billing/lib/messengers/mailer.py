from django.conf import settings
from django.core.mail import mail_managers, send_mail
from django.template.loader import render_to_string


class Mailer:
    @staticmethod
    def mail_managers(subject, template, data):
        mail_managers(
            subject=subject,
            message='',
            html_message=render_to_string(template, data))

    @staticmethod
    def mail_client(subject, template, data, email=None, client=None):
        send_mail(
            recipient_list=[email] if email else [client.email],
            from_email=settings.DEFAULT_FROM_EMAIL,
            subject='{prefix}{text}'.format(
                prefix=settings.EMAIL_SUBJECT_PREFIX, text=subject),
            message='',
            html_message=render_to_string(template, data))
