"""
Django settings for billing project.
"""

import os

import raven
from celery.schedules import crontab
from kombu import Queue

from .custom import MB_CLIENT_DISABLED_SECOND_EMAIL_DAYS
from .env import ENV, ROOT

SITE_ROOT = ROOT()
BASE_DIR = SITE_ROOT

DATABASES = {'default': ENV.db()}

locals().update(ENV.email())
DEFAULT_FROM_EMAIL = ENV.str('DEFAULT_FROM_EMAIL')
SERVER_EMAIL = ENV.str('SERVER_EMAIL')

ADMINS = [(x, x) for x in ENV.tuple('ADMINS')]
MANAGERS = ADMINS

SECRET_KEY = ENV.str('SECRET_KEY')
ALLOWED_HOSTS = ENV.list('ALLOWED_HOSTS')

DEBUG = ENV.bool('DEBUG')
TEMPLATE_DEBUG = ENV.bool('TEMPLATE_DEBUG')
TESTS = ENV.bool('TESTS', default=False)

# Celery
CELERY_LOGLEVEL = ENV.str('CELERY_LOGLEVEL')
BROKER_URL = ENV.str('BROKER_URL')
CELERY_RESULT_BACKEND = ENV.str('CELERY_RESULT_BACKEND')
CELERY_ALWAYS_EAGER = ENV.bool('CELERY_ALWAYS_EAGER', default=False)
CELERY_EAGER_PROPAGATES_EXCEPTIONS = ENV.bool(
    'CELERY_EAGER_PROPAGATES_EXCEPTIONS', default=False)
if ENV.str('BROKER_BACKEND', default=None):
    BROKER_BACKEND = ENV.str('BROKER_BACKEND')

# Django-cors
CORS_ORIGIN_ALLOW_ALL = ENV.bool('CORS_ORIGIN_ALLOW_ALL', default=False)
CORS_ORIGIN_REGEX_WHITELIST = []
for domain in ENV.list('CORS_ORIGIN_REGEX_WHITELIST', default=[]):
    CORS_ORIGIN_REGEX_WHITELIST.append(
        r'^(https?:\/\/)?([a-zA-Z0-9\-]+\.)?{}$'.format(domain))

# Application definition
INSTALLED_APPS = [
    'djmoney',
    'corsheaders',
    'raven.contrib.django.raven_compat',
    'adminactions',
    'modeltranslation',
    'admin_view_permission',
    'django.contrib.admin',
    'django.contrib.humanize',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'debug_toolbar',
    'django_extensions',
    'reversion',
    'rainbowtests',
    'django_otp',
    'django_otp.plugins.otp_static',
    'django_otp.plugins.otp_totp',
    'two_factor',
    'ajax_select',
    'rest_framework',
    'rest_framework.authtoken',
    'rosetta',
    'ordered_model',
    'cities_light',
    'django_filters',
    'django_admin_row_actions',
    'prettyjson',
    'annoying',
    'tabbed_admin',
    'rangefilter',
    'rest_framework_swagger',
    'djmoney.contrib.exchange',
    'timezone_field',
    'rest_framework_filters',

    # mb apps
    'finances',
    'billing',
    'clients',
    'hotels',
    'fms',
    'users',
]

SITE_ID = 1

MIDDLEWARE = [
    'django.middleware.gzip.GZipMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django_otp.middleware.OTPMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'billing.middleware.WhodidMiddleware',
    'billing.middleware.DisableAdminI18nMiddleware',
    'reversion.middleware.RevisionMiddleware',
]

ROOT_URLCONF = 'billing.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'billing/templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'billing.wsgi.application'

# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME':
        'django.contrib.auth.password_validation.\
UserAttributeSimilarityValidator',
    },
    {
        'NAME':
        'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME':
        'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME':
        'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'en'

LANGUAGES = (
    ('en', 'English'),
    ('ru', 'Russian'),
    ('de', 'German'),
    ('fr', 'French'),
    ('tr', 'Turkish'),
)
MODELTRANSLATION_LANGUAGES = ('en', 'ru')

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_URL = '/static/'

MEDIA_URL = '/media/'

INTERNAL_IPS = ['127.0.0.1']

STATIC_ROOT = os.path.join(BASE_DIR, 'static/')

MEDIA_ROOT = os.path.join(BASE_DIR, 'media/')

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'billing/static'),
    os.path.join(BASE_DIR, 'node_modules'),
)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

FIXTURE_DIRS = (os.path.join(BASE_DIR, 'fixtures'), )
LOCALE_PATHS = (
    os.path.join(os.path.dirname(os.path.dirname(__file__)), "locale"),
    os.path.join(os.path.dirname(os.path.dirname(__file__)), "app_locale"),
)

EMAIL_SUBJECT_PREFIX = 'Maxi-booking: '
DATA_UPLOAD_MAX_NUMBER_FIELDS = 10240

AUTHENTICATION_BACKENDS = ['users.auth_backends.ProxiedModelBackend']

# Logs
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'root': {
        'level': 'WARNING',
        'handlers': ENV.list('LOGGING', default=[])
    },
    'formatters': {
        'verbose': {
            'format':
            "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            'datefmt': "%d/%b/%Y %H:%M:%S"
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        }
    },
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'logs/billing.log',
            'formatter': 'verbose'
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'filters': ['require_debug_false'],
            'formatter': 'verbose'
        },
        'sentry': {
            'level': 'ERROR',
            'class':
            'raven.contrib.django.raven_compat.handlers.SentryHandler',
            'filters': ['require_debug_false'],
            'tags': {
                'custom-tag': 'x'
            },
        },
        # 'watchtower': {
        #     'level': 'ERROR',
        #     'filters': ['require_debug_false'],
        #     'class': 'watchtower.CloudWatchLogHandler',
        #     'formatter': 'simple'
        # },
    },
    'loggers': {
        'billing': {
            'handlers': ['file', 'mail_admins', 'sentry'],
            'level': 'DEBUG',
        },
    }
}
if not ENV.list('LOGGING', default=False):
    LOGGING.pop('root', None)
    LOGGING['loggers']['billing']['handlers'].remove('sentry')
    del LOGGING['handlers']['sentry']

# Two factor auth
LOGIN_URL = 'two_factor:login'
LOGOUT_URL = "admin:logout"
LOGIN_REDIRECT_URL = 'admin:index'

# Celery
CELERY_SEND_TASK_ERROR_EMAILS = True
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Europe/Dublin'
CELERY_APP = 'billing'
CELERY_QUEUES = (
    Queue('default'),
    Queue('priority_high'),
)
CELERY_DEFAULT_QUEUE = 'default'
CELERYD_TASK_SOFT_TIME_LIMIT = 60 * 5
CELERYBEAT_SCHEDULE = {
    'client_services_update_task': {
        'task': 'clients.tasks.client_services_update',
        'schedule': 60 * 10
    },
    'client_services_activation_task': {
        'task': 'clients.tasks.client_services_activation',
        'schedule': 60 * 10
    },
    'orders_payment_notify_task': {
        'task': 'finances.tasks.orders_payment_notify',
        'schedule': 60 * 60 * 24
    },
    'orders_clients_disable': {
        'task': 'finances.tasks.orders_clients_disable',
        'schedule': 60 * 10
    },
    'update_exchange_rates': {
        'task': 'finances.tasks.update_exchange_rates_task',
        'schedule': 60 * 60 * 24
    },
    'clients_archivation': {
        'task': 'clients.tasks.clients_archivation',
        'schedule': 60 * 10
    },
    'comments_uncompleted': {
        'task': 'billing.tasks.mail_comments_action_task',
        'schedule': crontab(minute=0, hour='6, 14, 18')
    },
    'clients_disabled_email_first': {
        'task': 'clients.tasks.client_disabled_email',
        'schedule': 60 * 60 * 24
    },
    'clients_disabled_email_second': {
        'task': 'clients.tasks.client_disabled_email',
        'schedule': 60 * 60 * 24,
        'args': (MB_CLIENT_DISABLED_SECOND_EMAIL_DAYS, )
    },
}

# Django phonenumber
PHONENUMBER_DB_FORMAT = 'INTERNATIONAL'

# Tests
TEST_RUNNER = 'rainbowtests.test.runner.RainbowDiscoverRunner'

# Django restframework
REST_FRAMEWORK = {
    'DEFAULT_VERSION':
    '1.0',
    'DEFAULT_VERSIONING_CLASS':
    'rest_framework.versioning.AcceptHeaderVersioning',
    'DEFAULT_PAGINATION_CLASS':
    'billing.pagination.StandardPagination',
    'DEFAULT_PERMISSION_CLASSES': [
        'billing.permissions.DjangoModelPermissionsGet',
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_FILTER_BACKENDS': (
        # 'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework_filters.backends.RestFrameworkFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    )
}

# Cities light
CITIES_LIGHT_TRANSLATION_LANGUAGES = ['en', 'ru']
CITIES_LIGHT_APP_NAME = 'hotels'

if not DEBUG and ENV.list('LOGGING', default=False):  # pragma: no cover
    # Sentry raven
    RAVEN_CONFIG = {
        'dsn': 'https://52126dbda9494c668b7b9dff7722c901:\
31b56314232c436fb812b98568a5f589@sentry.io/200649',
        'release': raven.fetch_git_sha(os.path.dirname(os.pardir)),
    }

# Django money
DEFAULT_CURRENCY = 'EUR'
BASE_CURRENCY = 'EUR'
# CURRENCIES = ('RUB', 'EUR', 'CAD', 'USD')
EXCHANGE_BACKEND = 'djmoney.contrib.exchange.backends.FixerBackend'

# Cache
CACHES = {'default': ENV.cache()}
CACHES['default']['TIMEOUT'] = 60 * 60 * 24 * 7

# DRM estensions
REST_FRAMEWORK_EXTENSIONS = {
    'DEFAULT_CACHE_RESPONSE_TIMEOUT': 60 * 60 * 24 * 7,
    'DEFAULT_CACHE_ERRORS': False,
    'DEFAULT_USE_CACHE': 'default'
}

# View permission
ADMIN_VIEW_PERMISSION_MODELS = [
    'finances.Order',
    'finances.Discount',
]

# Django tabbed admin
TABBED_ADMIN_USE_JQUERY_UI = True
