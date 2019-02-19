DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'billing',
        'USER': 'billing',
        'PASSWORD': 'billing',
        'HOST': '127.0.0.1',
        'PORT': '5432'
    }
}

EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.example.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'admin'
EMAIL_HOST_PASSWORD = 'password'
DEFAULT_FROM_EMAIL = 'maxibooking.group <admin@example.ru>'
SERVER_EMAIL = 'maxibooking.group <admin@example.ru>'

ADMINS = (('maxibooking.group', 'admin@example.com'), )
MANAGERS = ADMINS

SECRET_KEY = 'my_super_secret_key'
ALLOWED_HOSTS = ['127.0.0.1', 'localhost']
DEBUG = True

CELERY_LOGLEVEL = 'debug'
BROKER_URL = 'redis://localhost:6379'
CELERY_RESULT_BACKEND = 'redis://localhost:6379'

# Django-cors
CORS_ORIGIN_ALLOW_ALL = True

# MB setting by country
MB_SETTINGS_BY_COUNTRY = {}

# Client login restrictions
MB_CLIENT_LOGIN_RESTRICTIONS = [
    'support', 'demo', 'mail', 'mx', 'payment', 'www', 'new', 'info', 'cdn',
    'mb', 'help', 'redmine', 'deploy', 'trial', '_amazonses', 'billing',
    'maxibooking'
]

# Django money
FIXER_ACCESS_KEY = 'the secret key'

# Rbk
RBK_SHOP_ID = 'rbk_shop_id'
RBK_SECRET_KEY = 'rbk_secret_key'

# Paypal
PAYPAL_CLIENT_ID = 'paypal_client_id'
PAYPAL_SECRET = 'paypal_secret'

# Sberbank
SBERBANK_API_TOKEN = 'api_token'
SBERBANK_SECRET_KEY = 'secret_key'
SBERBANK_BASE_URL = 'https://securepayments.sberbank.ru/payment/'
SBERBANK_URL = SBERBANK_BASE_URL + 'docsite/assets/js/ipay.js'

SBERBANK_REST_USER = 'user'
SBERBANK_REST_PASSWORD = 'password'
SBERBANK_REST_URL = SBERBANK_BASE_URL + '/rest/'

# Stripe
MB_SETTINGS_BY_COUNTRY['STRIPE_PUBLISHABLE_KEY'] = {
    '__all__': 'stripe_publishable_key',
}
MB_SETTINGS_BY_COUNTRY['STRIPE_SECRET_KEY'] = {
    '__all__': 'stripe_secret_key',
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

# Billing
PAYMENT_SYSTEMS = (
    'stripe',
    'braintree',
    'braintree-subscription',
    'paypal',
    'rbk',
    'sberbank',
    'bill',
)

# Maxibooking urls
MB_SETTINGS_BY_COUNTRY['MB_URLS'] = {
    'ru': {
        'install': 'https://www.example.com',
        'login_invalidation': 'https://www.example.com',
        'archive': 'https://www.example.com',
        'fixtures': 'https://{}.example.com',
        'client_invalidation': 'https://{}.example.com',
        'token': 'token_ru'
    },
    '__all__': {
        'install': 'https://example.com',
        'login_invalidation': 'https://www.example.com',
        'archive': 'https://example.com',
        'fixtures': 'https://{}.example.com',
        'client_invalidation': 'https://{}.example.com',
        'token': 'token_all'
    }
}
MB_COUNTRIES_OVERWRITE = {}

# Requests timeout (sec)
MB_TIMEOUT = 1
# Order expired period (in days)
MB_ORDER_EXPIRED_DAYS = 21
# Order creation period (in days)
MB_ORDER_BEFORE_DAYS = 14
# Order payment notify (days before expiration)
MB_ORDER_PAYMENT_NOTIFY_DAYS = 3
# The number of days after blocking for sending email to the disabled clients
MB_CLIENT_DISABLED_FIRST_EMAIL_DAYS = 3
MB_CLIENT_DISABLED_SECOND_EMAIL_DAYS = 8
# The number of days after registration for sending email to the trial clients
MB_CLIENT_GREETING_EMAIL_DAYS = 8
# Client archive period (in months)
MB_CLIENT_ARCHIVE_MONTHS = 6
# Bill recipient company
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
