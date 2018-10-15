import pytest
from django.contrib.auth.models import User

pytestmark = pytest.mark.django_db


def test_profile_code_generate():
    user = User.objects.create_user(
        username='Bob',
        email='bob@example.com',
        password='password',
    )
    assert user.profile is not None
    assert user.profile.code[0] == str(user.id)
