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

MANAGERS = ADMINS
TESTS = True

MB_URL = 'https://example.com'
MB_ARCHIVE_URL = 'https://example.com'
MB_FIXTURES_URL = 'https://example.com'
MB_TIMEOUT = 1
MB_ORDER_EXPIRED_DAYS = 21
MB_ORDER_BEFORE_DAYS = 14
MB_ORDER_PAYMENT_NOTIFY_DAYS = 3
MB_CLIENT_ARCHIVE_MONTHS = 6
