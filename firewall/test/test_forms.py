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
            })

    def test_form_valid_request(self):
        """
        Test form save method
        """
        form = RuleForm({
            'name': 'new name',
            'url': '/test/',
        }, self.rule)
        self.assertTrue(form.is_valid())
        rule = form.save()
        self.assertEqual(rule.name, 'new name')
        self.assertEqual(rule.url, '/test/')
