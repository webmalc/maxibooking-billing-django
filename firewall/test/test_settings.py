from importlib import reload

from django.test import TestCase, override_settings

from firewall import settings as s


class SettingsTestCase(TestCase):
    """
    Settings tests
    """

    def test_default_settings(self):
        self.assertTrue(s.FIREWALL_ALLOW_BY_DEFAULT)
        self.assertEquals(s.FIREWALL_CACHE_TIMEOUT, 60 * 60 * 24)
        self.assertEquals(s.FIREWALL_CACHE_KEY, 'firewall_rules')

    @override_settings(
        FIREWALL_CACHE_KEY='firewall_new_rules',
        FIREWALL_CACHE_TIMEOUT=None,
        FIREWALL_ALLOW_BY_DEFAULT=False,
    )
    def test_override_settings(self):
        reload(s)
        self.assertFalse(s.FIREWALL_ALLOW_BY_DEFAULT)
        self.assertEquals(s.FIREWALL_CACHE_TIMEOUT, None)
        self.assertTrue(s.FIREWALL_CACHE_KEY, 'firewall_new_rules')
