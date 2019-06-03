import logging

from django.conf import settings
from django.core.mail import mail_managers as base_mail_managers
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _

from billing.lib.lang import select_locale


def mail_managers(subject, data=None, template='emails/base_manager.html'):
    base_mail_managers(subject=subject,
                       message='',
                       html_message=render_to_string(template,
                                                     data if data else {}))
    logging.getLogger('billing').info(
        'Send mail to managers. Subject: {}'.format(subject))


def mail_client(subject, template, data, email=None, client=None, lang=None):
    """
    Send a email to the client
    """
    with select_locale(client, lang):
        subject_text = settings.EMAIL_SUBJECT_PREFIX
        if client and client.name:
            subject_text += client.name + ', '
        subject_text += str(_(subject))

        send_mail(recipient_list=[email] if email else [client.email],
                  from_email=settings.DEFAULT_FROM_EMAIL,
                  subject=subject_text,
                  message='',
                  html_message=render_to_string(template, data))

    logging.getLogger('billing').info(
        'Send mail to client. Subject: {}; client: {}; email: {};'.format(
            subject, client, email))
