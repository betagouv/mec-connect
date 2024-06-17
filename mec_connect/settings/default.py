from __future__ import annotations

import sys
from pathlib import Path

from environ import Env

BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BASE_DIR / "mec_connect"))

env = Env()
ENVIRONMENT = env.str("ENVIRONMENT", default="dev")

dotenv_file = BASE_DIR / ".env"
if ENVIRONMENT != "testing" and dotenv_file.exists():
    env.read_env(dotenv_file)

SECRET_KEY = env.str("SECRET_KEY")
DEBUG = env.bool("DEBUG", False)
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["*"])
ROOT_URLCONF = "mec_connect.urls"
WSGI_APPLICATION = "mec_connect.wsgi.application"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

#
# Static files
#
STATIC_ROOT = BASE_DIR / "static"
STATIC_URL = "/static/"

#
# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/
#
LANGUAGE_CODE = "fr"
TIME_ZONE = "Europe/Paris"
USE_I18N = True
USE_TZ = True

#
# Application definition
#
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_extensions",
    "main",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

#
# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases
#
DATABASES = {"default": env.db()}

#
# Authentication
# https://simpleisbetterthancomplex.com/tutorial/2016/07/22/how-to-extend-django-user-model.html#abstractbaseuser
#
AUTH_USER_MODEL = "main.User"

#
# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators
#
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

#
# Celery Configuration Options
# https://docs.celeryproject.org/en/stable/userguide/configuration.html
#
CELERY_TIMEZONE = "Europe/Paris"
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60
CELERY_BROKER_URL = env.str("BROKER_URL")
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True
CELERY_ALWAYS_EAGER = env.bool("CELERY_ALWAYS_EAGER", default=False)

#
# Webhook security
#
WEBHOOK_SECRET = env.str("WEBHOOK_SECRET")

#
# Recoco API congiguration
#
RECOCO_API_URL = env.str("RECOCO_API_URL")
RECOCO_API_USERNAME = env.str("RECOCO_API_USERNAME")
RECOCO_API_PASSWORD = env.str("RECOCO_API_PASSWORD")
