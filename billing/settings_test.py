from .settings import *

LOGGING.pop('root', None)
# LOGGING['loggers']['billing']['handlers'].remove('file')

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

CELERY_ALWAYS_EAGER = True
CELERY_EAGER_PROPAGATES_EXCEPTIONS = True
BROKER_BACKEND = 'memory'

ADMINS = (('admin', 'admin@example.com'), ('manager', 'manager@example.com'))

MANAGERS = ADMINS
TESTS = True

CORS_ORIGIN_ALLOW_ALL = True

DEBUG = False
TEMPLATE_DEBUG = False

PAYMENT_SYSTEMS = (
    'braintree',
    'braintree-subscription',
    'paypal',
    'stripe',
    'rbk',
    'sberbank',
    'sberbank-rest',
    'bill',
)

# Django money
FIXER_ACCESS_KEY = 'the secret key'

# MB setting by country
MB_SETTINGS_BY_COUNTRY = {}

# Rbk
RBK_SHOP_ID = 'rbk_shop_id'
RBK_SECRET_KEY = 'rbk_secret_key'

# Paypal
PAYPAL_CLIENT_ID = 'paypal_client_id'
PAYPAL_SECRET = 'paypal_secret'

# Sberbank
SBERBANK_API_TOKEN = 'sberbank_api_token'
SBERBANK_SECRET_KEY = 'sberbank_secret_key'
SBERBANK_BASE_URL = 'http://sberbank.url'
SBERBANK_URL = SBERBANK_BASE_URL + 'docsite/assets/js/ipay.js'

SBERBANK_REST_USER = 'sberbank-api'
SBERBANK_REST_PASSWORD = 'sberbank'
SBERBANK_REST_URL = SBERBANK_BASE_URL + '/rest/'

# Stripe
MB_SETTINGS_BY_COUNTRY['STRIPE_PUBLISHABLE_KEY'] = {
    '__all__': 'stripe_publishable_key_all',
    'ae': 'stripe_publishable_key_ae'
}
MB_SETTINGS_BY_COUNTRY['STRIPE_SECRET_KEY'] = {
    '__all__': 'stripe_secret_key_all',
    'ae': 'stripe_secret_key_ae'
}

# Braintree
MB_SETTINGS_BY_COUNTRY['BRAINTREE_MERCHANT_ID'] = {
    '__all__': 'braintree_merchant_id',
}
MB_SETTINGS_BY_COUNTRY['BRAINTREE_PUBLIC_KEY'] = {
    '__all__': 'braintree_public_key',
}
MB_SETTINGS_BY_COUNTRY['BRAINTREE_PRIVATE_KEY'] = {
    '__all__': 'braintree_private_key',
}

MB_SETTINGS_BY_COUNTRY['MB_URLS'] = {
    'ru': {
        'install': 'http://www.example.com',
        'login_invalidation': 'http://www.example.com',
        'archive': 'http://www.example.com',
        'fixtures': '{}/fixtures',
        'client_invalidation': '{}/',
        'token': 'token_ru'
    },
    '__all__': {
        'install': 'http://example.com',
        'login_invalidation': 'http://www.example.com',
        'archive': 'http://example.com',
        'fixtures': '{}/fixtures',
        'client_invalidation': '{}/',
        'token': 'token_all'
    }
}
MB_COUNTRIES_OVERWRITE = {}
MB_TIMEOUT = 1
MB_ORDER_EXPIRED_DAYS = 21
MB_ORDER_BEFORE_DAYS = 14
MB_ORDER_PAYMENT_NOTIFY_DAYS = 3
MB_CLIENT_ARCHIVE_MONTHS = 6
MB_CLIENT_DISABLED_FIRST_EMAIL_DAYS = 3
MB_CLIENT_DISABLED_SECOND_EMAIL_DAYS = 8
MB_CLIENT_GREETING_EMAIL_DAYS = 8
MB_BILL_RECIPIENT_COMPANY = {
    'bank': 'bank title',
    'bank_bik': '1111111111111111111',
    'bank_account': '1111111111111111111',
    'inn': '1111111111111111111',
    'kpp': '1111111111111111111',
    'company_account': '1111111111111111111',
    'company_name': 'company name',
    'company_text': 'recipient text',
    'boss': 'Boss F.A.',
    'bookkeeper': 'Bookkeeper F.A.',
}
MB_CLIENT_LOGIN_RESTRICTIONS = [
    'support', 'demo', 'mail', 'mx', 'payment', 'www', 'new', 'info', 'cdn',
    'mb', 'help', 'redmine', 'deploy', 'trial', '_amazonses', 'billing',
    'maxibooking'
]
