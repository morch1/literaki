import os
from dotenv import load_dotenv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')

TEST_SERVER = bool(int(os.getenv('TEST_SERVER', False)))
SECRET_KEY = os.getenv('SECRET_KEY')

RECAPTCHA_PUBLIC_KEY = os.getenv('RECAPTCHA_SITE_KEY')
RECAPTCHA_PRIVATE_KEY = os.getenv('RECAPTCHA_SECRET_KEY')
RECAPTCHA_REQUIRED_SCORE = 0.85

if TEST_SERVER:
    DEBUG = True
    ALLOWED_HOSTS = ['localhost', '127.0.0.1', '[::1]', '192.168.100.11', '10.8.0.6', 'x.morchkovalski.com']
    STATIC_URL = '/static/'
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'local' / 'db.sqlite3',
        }
    }
    CHANNEL_LAYERS = {
        "default": {
            "BACKEND": "channels.layers.InMemoryChannelLayer"
        }
    }
else:
    DEBUG = False
    ALLOWED_HOSTS = ['demo.morchkovalski.com']
    STATIC_ROOT = '/srv/static.morchkovalski.com/literaki'
    STATIC_URL = 'https://static.morchkovalski.com/literaki'
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
    STATICFILES_FINDERS = (
        'django.contrib.staticfiles.finders.FileSystemFinder',
        'django.contrib.staticfiles.finders.AppDirectoriesFinder',
        'compressor.finders.CompressorFinder',
    )
    COMPRESS_ENABLED = True
    COMPRESS_OFFLINE = True
    COMPRESS_CSS_FILTERS = ['compressor.filters.css_default.CssAbsoluteFilter', 'compressor.filters.cssmin.CSSMinFilter']
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': os.getenv('DB_NAME'),
            'USER': os.getenv('DB_USER'),
            'PASSWORD': os.getenv('DB_PASSWORD'),
            'HOST': os.getenv('DB_HOST'),
            'PORT': os.getenv('DB_PORT'),
        },
    }
    CHANNEL_LAYERS = {
        'default': {
            'BACKEND': 'channels_redis.core.RedisChannelLayer',
            'CONFIG': {
                "hosts": [('127.0.0.1', 6379)],
            },
        },
    }

MAX_PLAYERS = int(os.getenv('MAX_PLAYERS', 4))

INSTALLED_APPS = [
    'captcha',
    'literakiapp.apps.LiterakiappConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'channels',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'literakiapp.middleware.player_middleware',
]

ROOT_URLCONF = 'literaki.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'literaki.wsgi.application'
ASGI_APPLICATION = "literaki.asgi.application"

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True
