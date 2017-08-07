from .settings import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'test_ndptc'
    }
}

LOGGING.pop('root', None)
CELERY_ALWAYS_EAGER = True

MB_URL = 'http://example.com'
