# -*- coding: utf-8 -*-
"""
Django firewall model classes
"""
from ipaddress import ip_address, ip_network, summarize_address_range

from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import ugettext_lazy as _
from ordered_model.models import OrderedModel

from .managers import IpRangeManager, RuleManager
from .settings import FIREWALL_CACHE_KEY


class CommonMixin(models.Model):
    """
    Base model
    """
    objects = IpRangeManager()

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


class IpRange(CommonMixin):
    """
    Ip model
    """
    start_ip = models.GenericIPAddressField(
        db_index=True,
        verbose_name=_('start ip'),
    )
    end_ip = models.GenericIPAddressField(
        db_index=True,
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
    rule = models.ForeignKey(
        'firewall.Rule',
        null=True,
        blank=True,
        db_index=True,
        on_delete=models.CASCADE,
        verbose_name=_('rule'),
        related_name='ip_ranges',
    )
    group = models.ForeignKey(
        'firewall.Group',
        null=True,
        blank=True,
        db_index=True,
        on_delete=models.CASCADE,
        verbose_name=_('group'),
        related_name='ip_ranges',
    )

    def get_networks(self):
        """
        Get networks
        """
        start_ip = ip_address(self.start_ip)
        if self.end_ip:
            end_ip = ip_address(self.end_ip)
            return [ip for ip in summarize_address_range(start_ip, end_ip)]
        return [ip_network(start_ip)]

    def __str__(self):
        networks = self.get_networks()
        title = '#{} - '.format(self.pk)
        title += ', '.join(map(str, networks[:5]))
        return title if len(networks) <= 6 else title + '...'

    def clean(self):
        """
        Additional validation
        """
        start = self.start_date
        end = self.end_date
        if start and end and start > end:
            raise ValidationError(
                _('End date should be greater than start date'))
        if not self.group and not self.rule:
            raise ValidationError(_('Empty rule and group'))
        try:
            self.get_networks()
        except ValueError as e:
            raise ValidationError(str(e))

    def validate_unique(self, exclude=None):
        """
        Additional unique validation
        """
        super().validate_unique(exclude)
        for s in ['group', 'rule']:
            val = getattr(self, s, None)
            if val:
                ip_count = val.ip_ranges.find_by_ip(
                    self.start_ip, self.end_ip, exclude_pk=self.pk).count()
                if ip_count:
                    raise ValidationError(
                        _('Ip range with this start ip, end ip, %(model)s \
                        already exist') % {'model': s})

    class Meta:
        verbose_name_plural = _('Ip ranges')
        ordering = ['-modified', '-created']


class Group(CommonMixin, TitleDescriptionMixin):
    """
    Ip group
    """
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
    is_allow = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name=_('is allow'),
        help_text=_('Allow or deny?'),
    )

    objects = RuleManager()

    class Meta(OrderedModel.Meta):
        pass
