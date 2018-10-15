import random
import string

from annoying.fields import AutoOneToOneField
from django.contrib.auth.models import User
from django.core.validators import MinLengthValidator
from django.db import models
from django_extensions.db.models import TimeStampedModel

from billing.models import CommonInfo


class Profile(CommonInfo, TimeStampedModel):
    """
    User profile class
    """
    user = AutoOneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
    )
    code = models.CharField(
        max_length=10,
        blank=True,
        null=False,
        unique=True,
        validators=[MinLengthValidator(3)],
        help_text='The unique user`s code',
    )

    def generate_code(self):
        """
        Generate a unique code for user
        """
        code = ''.join(
            random.choices(string.ascii_lowercase + string.digits, k=5))
        self.code = '{}{}'.format(self.user.id, code)

    def __str__(self):
        return '{}`s profile'.format(self.user)
