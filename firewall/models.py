# -*- coding: utf-8 -*-
"""
Django firewall model classes
"""
from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _
from ordered_model.models import OrderedModel

from .managers import RuleManager


class EntriesField(models.TextField):
    """
    Ip/domain list field
    """
    description = 'Ip/domain list'

    def __init__(self, *args, **kwargs):
        kwargs['verbose_name'] = _('ip/domain list')
        kwargs['help_text'] = ('One ip, ip address range or domain per line. \
Example: 127.0.0.0/24')
        super(EntriesField, self).__init__(*args, **kwargs)


class CommonMixin(models.Model):
    """
    Base model
    """
    name = models.CharField(
        max_length=255,
        db_index=True,
        unique=True,
        verbose_name=_('name'),
    )
    description = models.TextField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name=_('description'),
    )
    is_enabled = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name=_('is enabled'),
    )
    created = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        editable=False,
        verbose_name=_('created'),
    )
    modified = models.DateTimeField(
        auto_now=True,
        db_index=True,
        editable=False,
        verbose_name=_('modified'),
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        db_index=True,
        editable=False,
        on_delete=models.CASCADE,
        verbose_name=_('created by'),
        related_name='%(app_label)s_%(class)s_created_by',
    )
    modified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        db_index=True,
        on_delete=models.CASCADE,
        editable=False,
        verbose_name=_('modified by'),
        related_name='%(app_label)s_%(class)s_modified_by',
    )

    def __str__(self):
        return self.name

    class Meta:
        abstract = True


class Group(CommonMixin):
    """
    Ip/domain group
    """
    entries = EntriesField(db_index=True)
    rules = models.ManyToManyField(
        'firewall.Rule', verbose_name=_('rules'), blank=True)

    class Meta:
        ordering = ('name', )


class Rule(CommonMixin, OrderedModel):
    """
    Firewall rules
    """
    url = models.CharField(
        max_length=255,
        db_index=True,
        verbose_name=_('url'),
        help_text=_('Url regex pattern. Example: /admin/.*'),
    )
    entries = EntriesField(db_index=True, null=True, blank=True)
    groups = models.ManyToManyField(
        'firewall.Group',
        blank=True,
        verbose_name=_('ip/domain groups'),
        through=Group.rules.through,
    )
    is_allow = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name=_('is allow'),
        help_text=_('Allow or deny?'),
    )

    objects = RuleManager()

    class Meta(OrderedModel.Meta):
        pass
