DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'billing',
        'USER': 'postgres',
        'PASSWORD': 'postgres',
        'HOST': '127.0.0.1',
        'PORT': '5432'
    }
}

EMAIL_USE_TLS = False
EMAIL_HOST = 'info.maxi-booking.ru'
# EMAIL_PORT = 465
EMAIL_HOST_USER = 'robot@maxi-booking.ru'
EMAIL_HOST_PASSWORD = 'ghjlflbv10rjgbq'
DEFAULT_FROM_EMAIL = 'robot@maxi-booking.ru'
SERVER_EMAIL = 'robot@maxi-booking.ru'

ADMINS = (('webmalc', 'm@webmalc.pw'), )
MANAGERS = ADMINS

SECRET_KEY = 'my_super_secret_key'
ALLOWED_HOSTS = ['*']
DEBUG = True

CELERY_LOGLEVEL = 'debug'

# Maxibooking url
MB_URL = 'https://example.com'
# Maxibooking archive url
MB_ARCHIVE_URL = 'https://example.com'
# Maxibooking token
MB_TOKEN = 'my_super_secret_token'
# Requests timeout (sec)
MB_TIMEOUT = 1
# Order expired period (in days)
MB_ORDER_EXPIRED_DAYS = 21
# Order creation period (in days)
MB_ORDER_BEFORE_DAYS = 14
# Order payment notify (days before expiration)
MB_ORDER_PAYMENT_NOTIFY_DAYS = 3
# Client archive period (in months)
MB_CLIENT_ARCHIVE_MONTHS = 6
