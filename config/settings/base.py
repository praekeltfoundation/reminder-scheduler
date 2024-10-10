"""
Django settings for reminder-scheduler project.
"""

import os
from os.path import join

import dj_database_url
import environ
from celery.schedules import crontab
from kombu import Exchange, Queue

root = environ.Path(__file__) - 3
env = environ.Env(DEBUG=(bool, False))

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ROOT_DIR = root()
environ.Env.read_env(join(ROOT_DIR, ".env"))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env.str("SECRET_KEY", "dev_secret_key")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool("DEBUG", True)

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "celery",
    "django_celery_beat",
    "rest_framework",
    "scheduler",
    "quickreplies",
    "rapidpro_api",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "debug": env.bool("DEBUG", False),
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"


# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    "default": dj_database_url.config(
        default="sqlite:///{}".format(join(BASE_DIR, "db.sqlite3"))
    )
}


# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATICFILES_FINDERS = (
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
    "django.contrib.staticfiles.finders.FileSystemFinder",
)

STATIC_ROOT = join(ROOT_DIR, "staticfiles")
STATIC_URL = "/static/"
COMPRESS_ENABLED = True

# Configure Sentry Logging
SENTRY_DSN = env.str("SENTRY_DSN", "")

REST_FRAMEWORK = {
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 10,
}

# Celery configuration options
CELERY_RESULT_BACKEND = env.str("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")
CELERYBEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"

CELERY_BROKER_URL = env.str("CELERY_BROKER_URL", "redis://localhost:6379/0")
# BROKER_URL and REDIS_URL are required to have rabbitmq and redis monitoring.
# Redis is used in dev env, RabbitMQ on production.
BROKER_URL = env.str("CELERY_BROKER_URL", "redis://localhost:6379/0")
REDIS_HOST = env.str("REDIS_HOST", "localhost")
REDIS_PORT = env.str("REDIS_PORT", "6379")
REDIS_DB = env.str("REDIS_DB", "0")
REDIS_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"

CELERY_ALWAYS_EAGER = False

CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_ACCEPT_CONTENT = ["json"]

CELERYBEAT_SCHEDULE = {
    "reminder_check": {
        "task": "scheduler.tasks.check_for_scheduled_reminders",
        "schedule": crontab(minute="*"),
        "kwargs": {},
    },
}

TURN_AUTH_TOKEN = env.str("TURN_AUTH_TOKEN", "")
TURN_URL = env.str("TURN_URL", "")
