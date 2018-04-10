# -*- coding: utf-8 -*-
"""
Django firewall forms classes
"""
from django import forms
from django.forms.models import BaseInlineFormSet

from .models import Rule
from .settings import FIREWALL_IPRANGES_ADMIN_MAX


class RuleForm(forms.ModelForm):
    class Meta:
        model = Rule
        exclude = ['created', 'modified', 'created_by', 'modified_by']


class IpRangeFormSet(BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.queryset = self.queryset.select_related(
            'created_by', 'modified_by')[:FIREWALL_IPRANGES_ADMIN_MAX]
