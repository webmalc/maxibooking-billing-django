from billing.lib.messengers.mailer import mail_client, mail_managers

from .celery import app
from .models import Comment


@app.task
def mail_comments_action_task():
    """
    Send a mail about uncompleted actions
    """
    comments = Comment.objects.get_uncompleted()
    for comment in comments:
        data = {
            'subject': 'Action not completed',
            'template': 'emails/comment_uncompleted.html',
            'data': {
                'comment': comment
            }
        }
        manager = comment.content_object.manager
        if manager:
            data['email'] = manager.email
            mail_client(**data)
        else:
            mail_managers(**data)
