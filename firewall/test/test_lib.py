from django.test import TestCase, override_settings

from ..models import Group, Rule


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
            entries='127.0.0.1',
        )
        group_one = Group.objects.create(name='group one')
        group_two = Group.objects.create(name='group two')

        rule.groups.add(group_one, group_two)

        def fetch():
            return list(Rule.objects.fetch())

        self.assertNumQueries(2, fetch)
        self.assertNumQueries(0, fetch)

        rule.name = 'new rule name'
        rule.save()

        self.assertNumQueries(2, fetch)
        self.assertNumQueries(0, fetch)
