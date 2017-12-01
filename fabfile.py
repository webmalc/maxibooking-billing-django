from fabric.api import cd, env, prefix, run, sudo

env.hosts = ['billing.maxi-booking.com']
env.port = 22
env.key_filename = '~/.ssh/maxibookingltd.pem'
env.user = "ubuntu"
env.project_dir = '/home/ubuntu/python/maxibooking-billing'
env.activate = 'source /home/ubuntu/.virtualenvs/billing/bin/activate'


def deploy():
    with cd(env.project_dir):
        with prefix(env.activate):
            run('git pull origin master')
            run('pip install --upgrade pip')
            run('pip install -r requirements.txt')
            run('npm install')
            run('./manage.py collectstatic --no-input')
            run('./manage.py migrate --no-input')
            run('./manage.py compilemessages')
    sudo('sudo supervisorctl restart billing')
    sudo('sudo supervisorctl restart billing_celery')
    sudo('sudo supervisorctl restart billing_celery_beat')
    sudo('sudo service nginx restart')
