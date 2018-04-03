from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from .models import Rule


class RuleForm(forms.ModelForm):
    class Meta:
        model = Rule
        exclude = ['created', 'modified', 'created_by', 'modified_by']

    def clean(self):
        """
        Additional validation
        """
        cleaned_data = super().clean()
        entries = cleaned_data.get('entries')
        groups = cleaned_data.get('groups')
        groups_count = groups.count() if groups else 0
        if not entries and not groups_count:
            raise ValidationError(
                _('At least one of the "ip list" or \
"ip groups" fields is required'))
