from django.test import TestCase

from ..forms import RuleForm
from ..models import Rule


class RuleFormTestCase(TestCase):
    """
    RuleForm tests
    """

    def setUp(self):
        self.rule = Rule.objects.create(
            name='test rule',
            url='/admin/.*',
            entries='127.0.0.1',
        )

    def test_form_invalid_request(self):
        """
        Test form validation
        """
        form = RuleForm({'created': 'invalid'}, self.rule)
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors, {
                'name': ['This field is required.'],
                'url': ['This field is required.'],
                '__all__': [
                    'At least one of the "ip list" or \
"ip groups" fields is required'
                ]
            })

    def test_form_valid_request(self):
        """
        Test form save method
        """
        form = RuleForm({
            'name': 'new name',
            'url': '/test/',
            'entries': '0.0.0.0',
        }, self.rule)
        self.assertTrue(form.is_valid())
        rule = form.save()
        self.assertEqual(rule.name, 'new name')
        self.assertEqual(rule.url, '/test/')
        self.assertEqual(rule.entries, '0.0.0.0')
