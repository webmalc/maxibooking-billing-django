from .settings import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'test_ndptc'
    }
}

LOGGING.pop('root', None)
CELERY_ALWAYS_EAGER = True

ADMINS = (('admin', 'admin@example.com'), ('manager', 'manager@example.com'))
MB_URL = 'http://example.com'

MANAGERS = ADMINS
