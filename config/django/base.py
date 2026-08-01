"""
Django settings for this project.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.2/ref/settings/
"""

import socket

from config.env import BASE_DIR, env
from config.settings.django_allauth import (
    ALLAUTH_INSTALLED_APPS,
    ALLAUTH_MIDDLEWARE,
)
from config.settings.wagtail import (
    WAGTAIL_INSTALLED_APPS,
    WAGTAIL_MIDDLEWARE,
    WAGTAIL_TEMPLATE_CONTEXT_PROCESSORS,
)

try:
    import django_stubs_ext

    django_stubs_ext.monkeypatch()
except ImportError:
    pass

env.read_env(BASE_DIR / ".env")

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env.str("SECRET_KEY", "")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool("DEBUG", default=True)

ALLOWED_HOSTS = ["*"]

# Application definition
INSTALLED_APPS = (
    WAGTAIL_INSTALLED_APPS
    + [
        "django_tasks",
        "src.feeds",
        "src.comments",
        "src.accounts",
        "debug_toolbar",
        "django_comments_xtd",
        "django_comments",
        "django.forms",
        "captcha",
        "django_htmx",
        "django.contrib.admin",
        "django.contrib.auth",
        "django_vite",
        "django.contrib.redirects",
        "polymorphic",
        "django.contrib.postgres",
        "django.contrib.sites",
        "django.contrib.contenttypes",
        "django.contrib.sessions",
        "django.contrib.messages",
        "django.contrib.staticfiles",
        "django.contrib.sitemaps",
        "health_check",
    ]
    + ALLAUTH_INSTALLED_APPS
)

MIDDLEWARE = (
    [
        "debug_toolbar.middleware.DebugToolbarMiddleware",
        "django_htmx.middleware.HtmxMiddleware",
        "django.contrib.redirects.middleware.RedirectFallbackMiddleware",
        "django.middleware.security.SecurityMiddleware",
        "django_permissions_policy.PermissionsPolicyMiddleware",
        "django.contrib.sessions.middleware.SessionMiddleware",
        "django.middleware.common.CommonMiddleware",
        "django.middleware.csrf.CsrfViewMiddleware",
        "django.contrib.auth.middleware.AuthenticationMiddleware",
        "django.contrib.messages.middleware.MessageMiddleware",
        "src.base.middleware.WagtailAwareContentSecurityPolicyMiddleware",
    ]
    + ALLAUTH_MIDDLEWARE
    + WAGTAIL_MIDDLEWARE
)

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            "src/templates",
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "src.base.context_processors.global_search_form",
                "src.base.context_processors.webrings_context",
                "django.template.context_processors.csp",
            ]
            + WAGTAIL_TEMPLATE_CONTEXT_PROCESSORS,
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env.str("DB_NAME", "wagtail"),
        "USER": env.str("DB_USER", "postgres"),
        "PASSWORD": env.str("DB_PASSWORD", "postgres"),
        "HOST": env.str("DB_HOST", "127.0.0.1"),
        "PORT": env.int("DB_PORT", 5432),
        "CONN_MAX_AGE": 0,
        "CONN_HEALTH_CHECKS": env.bool("CONN_HEALTH_CHECKS", True),
        "OPTIONS": {
            "pool": env.bool("DB_POOL", True),
        },
    }
}

# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators
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


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True
LANGUAGES = [
    ("en", "English"),
    ("ar", "Arabic"),
]

LOCALE_PATHS = [
    BASE_DIR / "locales",
]

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/
STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static", "public"]
STATIC_ROOT = "staticfiles"

# Handle upload files and media
# https://docs.djangoproject.com/en/5.2/topics/files/
MEDIA_ROOT = BASE_DIR / "media"
MEDIA_URL = "/media/"
DATA_UPLOAD_MAX_NUMBER_FIELDS = 10_000

STORAGES = {
    "default": {
        "BACKEND": "config.settings.django_storage.MediaR2Storage",
    },
    "staticfiles": {
        "BACKEND": "src.base.storage.ManifestStaticFilesStorage",
    },
    "wagtailrenditions": {
        "BACKEND": "config.settings.django_storage.WagtailRenditionStorage",
    },
}

SITE_ID = 1

WEBMENTION_DOMAIN = env.str("WEBMENTION_DOMAIN", "mahmoudashraf.dev")  # e.g., maw.sh
WEBMENTION_TOKEN = env.str("WEBMENTION_TOKEN", "")
LEGACY_SITE_DOMAIN = "maw.sh"

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": env.str("REDIS_LOCATION", ""),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "PASSWORD": env.str("REDIS_PASSWORD", ""),
        },
    }
}

CAPTCHA_IMAGE_SIZE = (80, 36)

REDIS_URL = env.str("REDIS_URL", "")

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

TASKS = {
    "default": {
        "BACKEND": "django_tasks.backends.immediate.ImmediateBackend",
    },
}


PERMISSIONS_POLICY = {
    "accelerometer": [],
    "ambient-light-sensor": [],
    "autoplay": ["self"],
    "camera": [],
    "display-capture": [],
    "encrypted-media": [],
    "fullscreen": [],
    "geolocation": [],
    "gyroscope": [],
    "interest-cohort": [],
    "magnetometer": [],
    "microphone": [],
    "midi": [],
    "payment": [],
    "usb": [],
}

INTERNAL_IPS = env.list(
    "INTERNAL_IPS",
    default=[
        "127.0.0.1",
        "172.17.0.0",
        "localhost",
    ],
)

try:
    hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())
    INTERNAL_IPS += [ip[:-1] + "1" for ip in ips if ip.count(".") == 3]
except Exception:
    pass

AUTH_USER_MODEL = "accounts.User"

DJANGO_ADMIN_PATH = env.str("DJANGO_ADMIN_PATH", "admin/")
WAGTAIL_ADMIN_PATH = env.str("WAGTAIL_ADMIN_PATH", "cms/")

TMDB_API_KEY = env.str("TMDB_API_KEY", "")

SILENCED_SYSTEM_CHECKS = ["wagtailadmin.W002"]

# lib settings
from config.settings.django_allauth import *  # noqa: E402, F403
from config.settings.django_comments_xtd import *  # noqa: E402, F403
from config.settings.django_storage import *  # noqa: E402, F403
from config.settings.vite import *  # noqa: E402, F403
from config.settings.wagtail import *  # noqa: E402, F403
