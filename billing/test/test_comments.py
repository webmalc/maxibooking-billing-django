import pytest
from django.conf import settings

from billing.models import Comment
from billing.tasks import mail_comments_action_task

pytestmark = pytest.mark.django_db


def test_comments_get_uncompleted(make_comments):
    comments = Comment.objects.get_uncompleted()
    assert comments.count() == 2
    assert comments[1].text == 'test action uncompleted comment 1'
    assert comments[0].text == 'test action uncompleted comment 2'


def test_mail_comments_action_task(make_comments, mailoutbox):
    mail_comments_action_task.delay()
    assert len(mailoutbox) == 2
    assert mailoutbox[1].recipients() == [m for r, m in settings.MANAGERS]
    assert mailoutbox[0].recipients() == ["test@example.com"]
    html = mailoutbox[0].alternatives[0][0]
    assert 'test action uncompleted comment 2' in html
