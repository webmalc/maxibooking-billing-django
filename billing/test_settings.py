from .settings import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'test_ndptc'
    }
}

CELERY_ALWAYS_EAGER = True

MB_URL = 'http://example.com'
