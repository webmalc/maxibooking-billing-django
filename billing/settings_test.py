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

CORS_ORIGIN_ALLOW_ALL = True

# Rbk
RBK_SHOP_ID = 'rbk_shop_id'
RBK_SECRET_KEY = 'rbk_secret_key'

# Stripe
STRIPE_PUBLISHABLE_KEY = 'stripe_publishable_key'
STRIPE_SECRET_KEY = 'stripe_secret_key'

MB_URLS = {
    'ru': {
        'install': 'https://www.example.com',
        'archive': 'https://www.example.com',
        'fixtures': 'https://www.example.com',
        'token': 'token_ru'
    },
    '__all__': {
        'install': 'https://example.com',
        'archive': 'https://example.com',
        'fixtures': 'https://example.com',
        'token': 'token_all'
    }
}
MB_TIMEOUT = 1
MB_ORDER_EXPIRED_DAYS = 21
MB_ORDER_BEFORE_DAYS = 14
MB_ORDER_PAYMENT_NOTIFY_DAYS = 3
MB_CLIENT_ARCHIVE_MONTHS = 6
