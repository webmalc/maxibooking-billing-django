from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_client_login_restrictions(value):
    restrictions = settings.MB_CLIENT_LOGIN_RESTRICTIONS
    if value in restrictions:
        raise ValidationError(
            _('invalid client login: ') + ', '.join(restrictions))
