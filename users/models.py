import random
import string

from annoying.fields import AutoOneToOneField
from django.contrib.auth.models import Group, User
from django.core.validators import (MaxValueValidator, MinLengthValidator,
                                    MinValueValidator, ValidationError)
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django_extensions.db.models import TimeStampedModel, TitleDescriptionModel

from billing.models import CommonInfo
from finances.validators import validate_code
from hotels.models import Country

from .managers import DepartmentManager, ProfileManager


class Department(CommonInfo, TimeStampedModel, TitleDescriptionModel):
    """
    Users department class
    """

    objects = DepartmentManager()

    default_group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        verbose_name=_('default group'),
        related_name='default_departments',
        null=True,
        blank=True,
        db_index=True)
    admin_group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        verbose_name=_('admin group'),
        related_name='admin_departments',
        null=True,
        blank=True,
        db_index=True)
    admin = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        verbose_name=_('admin'),
        db_index=True,
        related_name='admin_departments',
        null=True,
        blank=True)
    max_percentage_discount = models.FloatField(
        verbose_name=_('maximum percentage discount'),
        validators=[MinValueValidator(0),
                    MaxValueValidator(100)],
        db_index=True,
        null=True,
        blank=True)
    min_percentage_discount = models.FloatField(
        verbose_name=_('minimum percentage discount'),
        validators=[MinValueValidator(0),
                    MaxValueValidator(100)],
        db_index=True,
        null=True,
        blank=True)
    country = models.ForeignKey(
        Country,
        on_delete=models.SET_NULL,
        verbose_name=_('country'),
        null=True,
        blank=True,
        db_index=True)

    def clean(self):
        """
        Department validation
        """
        if not self.max_percentage_discount or\
           not self.min_percentage_discount:
            return None
        if self.min_percentage_discount > self.max_percentage_discount:
            raise ValidationError('The minimum discount cannot be greater \
than the maximum discount')

    class Meta:
        ordering = ['title']


class Profile(CommonInfo, TimeStampedModel):
    """
    User profile class
    """

    objects = ProfileManager()

    user = AutoOneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        verbose_name=_('department'),
        related_name='profiles',
        null=True,
        blank=True,
        db_index=True)
    code = models.CharField(
        max_length=20,
        blank=True,
        null=False,
        unique=True,
        validators=[MinLengthValidator(3), validate_code],
        help_text=_('The unique user`s code'),
    )

    def generate_code(self):
        """
        Generate a unique code for the user
        """
        code = ''.join(
            random.choices(string.ascii_lowercase + string.digits, k=5))
        self.code = '{}{}'.format(self.user.id, code)

    def __str__(self):
        return '{}`s profile'.format(self.user)


class BillingUser(User):
    """
    Django user model proxy
    """

    @property
    def profile(self):
        try:
            return super().profile
        except Profile.DoesNotExist:
            return None

    @property
    def department(self):
        return self.profile.department

    class Meta:
        proxy = True
