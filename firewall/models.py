# -*- coding: utf-8 -*-
"""
Django firewall model classes
"""
from django.conf import settings
from django.core.cache import cache
from django.db import models
from django.utils.translation import ugettext_lazy as _
from ordered_model.models import OrderedModel

from .managers import RuleManager
from .settings import FIREWALL_CACHE_KEY


class CommonMixin(models.Model):
    """
    Base model
    """
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

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        cache.delete(FIREWALL_CACHE_KEY)

    class Meta:
        abstract = True


class TitleDescriptionMixin(models.Model):
    """
    Title and description mixin
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

    def __str__(self):
        return self.name

    class Meta:
        abstract = True


class Ip(CommonMixin):
    """
    Ip model
    """
    start_ip = models.GenericIPAddressField(
        db_index=True,
        unique=True,
        verbose_name=_('start ip'),
    )
    end_ip = models.GenericIPAddressField(
        db_index=True,
        unique=True,
        blank=True,
        null=True,
        verbose_name=_('end ip'),
    )
    start_date = models.DateTimeField(
        db_index=True,
        blank=True,
        null=True,
        verbose_name=_('start date'),
    )
    end_date = models.DateTimeField(
        db_index=True,
        blank=True,
        null=True,
        verbose_name=_('end date'),
    )
    rules = models.ManyToManyField(
        'firewall.Rule',
        verbose_name=_('rules'),
        blank=True,
    )
    groups = models.ManyToManyField(
        'firewall.Group',
        verbose_name=_('groups'),
        blank=True,
    )

    def __str__(self):
        return self.ip

    class Meta:
        verbose_name_plural = _('IPs')
        unique_together = (('start_ip', 'end_ip'))
        ordering = ['start_ip', 'end_ip']


class Group(CommonMixin, TitleDescriptionMixin):
    """
    Ip group
    """
    ips = models.ManyToManyField(
        'firewall.Group',
        verbose_name=_('IPs'),
        related_name='group_ips',
    )
    rules = models.ManyToManyField(
        'firewall.Rule', verbose_name=_('rules'), blank=True)

    class Meta:
        ordering = ('name', )


class Rule(CommonMixin, TitleDescriptionMixin, OrderedModel):
    """
    Firewall rules
    """
    url = models.CharField(
        max_length=255,
        db_index=True,
        verbose_name=_('url'),
        help_text=_('Url regex pattern. Example: /admin/.*'),
    )
    groups = models.ManyToManyField(
        'firewall.Group',
        blank=True,
        verbose_name=_('ip groups'),
        through=Group.rules.through,
    )
    ips = models.ManyToManyField(
        'firewall.Group',
        verbose_name=_('IPs'),
        related_name='rules_ips',
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
