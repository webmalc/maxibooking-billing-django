from .settings import *

LOGGING.pop('root', None)
# LOGGING['loggers']['billing']['handlers'].remove('file')

CELERY_ALWAYS_EAGER = True
CELERY_EAGER_PROPAGATES_EXCEPTIONS = True
BROKER_BACKEND = 'memory'

ADMINS = (('admin', 'admin@example.com'), ('manager', 'manager@example.com'))

MANAGERS = ADMINS
TESTS = True

CORS_ORIGIN_ALLOW_ALL = True

DEBUG = False
TEMPLATE_DEBUG = False

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
