from django.test import TestCase, override_settings

from ..lib.firewall import Firewall
from ..models import Group, IpRange, Rule


@override_settings(
    CACHES={
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'django-firewall',
        }
    })
class RuleTestCase(TestCase):
    """
    Rule model tests
    """

    def test_fetch(self):
        rule = Rule.objects.create(
            name='test rule',
            url='/page/.*/',
        )
        group_one = Group.objects.create(name='group one')
        group_two = Group.objects.create(name='group two')

        rule.groups.add(group_one, group_two)

        def fetch():
            return list(Rule.objects.fetch())

        self.assertNumQueries(4, fetch)
        self.assertNumQueries(0, fetch)

        rule.name = 'new rule name'
        rule.save()

        self.assertNumQueries(4, fetch)
        self.assertNumQueries(0, fetch)


class FirewallTestCase(TestCase):
    """
    Firewall core class tests
    """

    def setUp(self):
        ip_range_all = IpRange.objects.create(start_ip='0.0.0.0')
        ip_range_localhost = IpRange.objects.create(start_ip='127.0.0.1')
        ip_range = IpRange.objects.create(
            start_ip='46.36.198.121',
            end_ip='46.36.198.125',
        )
        group = Group.objects.create(name='group')
        group.ip_ranges.add(ip_range)

        rule_admin_deny = Rule.objects.create(
            name='test admin deny rule',
            url='/admin/.*/',
            is_allow=False,
        )
        rule_admin_deny.top()
        rule_admin_deny.ip_ranges.add(ip_range_all)
        rule_admin_allow = Rule.objects.create(
            name='test admin allow rule',
            url='/admin/.*/',
            is_allow=True,
        )
        rule_admin_allow.groups.add(group)
        rule_admin_allow.ip_ranges.add(ip_range_localhost)

        rule_page = Rule.objects.create(
            name='test page rule',
            url='/page/somepage/',
            is_allow=False,
        )
        rule_page.ip_ranges.add(ip_range_localhost)

    # def test_check_by_lib(self):
    #     assert Firewall(ip='11.22.33.44', path='/').check()
    #     assert not Firewall(ip='11.22.33.44', path='/admin/testpage/').check()
    #     assert Firewall(ip='127.0.0.1', path='/admin/testpage/').check()
    #     assert Firewall(ip='46.36.198.121', path='/admin/testpage/').check()
    #     assert Firewall(ip='46.36.198.122', path='/admin/testpage/').check()
    #     assert not Firewall(ip='127.0.0.1', path='/page/somepage/').check()

    # def test_check_by_middleware(self):
    #     pass
