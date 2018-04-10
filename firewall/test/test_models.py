from datetime import timedelta

from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.test import Client, TestCase, override_settings
from django.utils import timezone

from ..admin import RuleAdmin
from ..models import Group, IpRange, Rule


@override_settings(MIDDLEWARE=[
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
])
class RuleAdminTestCase(TestCase):
    """
    RuleForm tests
    """

    def test_iprange_validation(self):
        group = Group.objects.create(name='group one')
        ip_range = IpRange()
        ip_range.start_ip = '12.22.33.44'
        ip_range.end_ip = '12.22.33.44'
        ip_range.group = group
        ip_range.full_clean()
        ip_range.save()
        with self.assertRaises(ValidationError):
            ip_range.start_date = timezone.now()
            ip_range.end_date = timezone.now() - timedelta(days=1)
            ip_range.full_clean()
        ip_range.end_date = timezone.now() + timedelta(days=1)
        ip_range.full_clean()
        ip_range.save()

        with self.assertRaises(ValidationError):
            ip_range.group = None
            ip_range.full_clean()

        with self.assertRaises(ValidationError):
            ip_range.pk = None
            ip_range.group = group
            ip_range.full_clean()

        ip_range.start_ip = '11.11.11.11'
        ip_range.full_clean()
        ip_range.save()

        self.assertEquals(2, group.ip_ranges.all().count())

        ip_range.pk = None
        ip_range.group = None
        ip_range.rule = Rule.objects.create(name='rule one')
        ip_range.full_clean()
        ip_range.save()

    def test_rules_list(self):
        username = 'test_admin'
        password = 'password'
        email = 'test@example.com'
        get_user_model().objects.create_superuser(
            username=username, password=password, email=email)
        client = Client()
        client.login(username=username, password=password)
        for i in range(1, 100):
            Rule.objects.create(
                name='test rule {}'.format(i),
                url='/page{}/.*/'.format(i),
            )
        url = reverse('admin:firewall_rule_changelist')

        self.assertNumQueries(9, lambda: client.get(url))
        response = client.get(url)
        self.assertContains(response, 'test rule 88')
        self.assertContains(response, 'page11/.*/')

    def test_get_groups(self):
        rule = Rule.objects.create(
            name='test rule',
            url='/page/.*/',
        )
        group_one = Group.objects.create(name='group one')
        group_two = Group.objects.create(name='group two')

        rule.groups.add(group_one, group_two)
        admin = RuleAdmin(Rule, AdminSite())
        route = 'admin:firewall_group_change'
        url_one = reverse(route, args=[group_one.pk])
        url_two = reverse(route, args=[group_two.pk])
        get_groups = admin.get_groups(rule)

        self.assertIn('group one', get_groups)
        self.assertIn('group two', get_groups)
        self.assertIn(url_one, get_groups)
        self.assertIn(url_two, get_groups)
