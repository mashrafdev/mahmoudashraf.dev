import sys

from django.utils.csp import CSP

from config.django.base import *  # noqa: F403
from config.env import env
from config.settings.wagtail_prod import *  # noqa: E402, F403

DEBUG = env.bool("DEBUG", default=False)

APPEND_SLASH = True

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=[])

CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS", default=[])
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True
SECURE_SSL_REDIRECT = env.bool("SECURE_SSL_REDIRECT", default=False)
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_NAME = "__Secure-sessionid"
CSRF_COOKIE_NAME = "__Secure-csrftoken"
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = "Lax"
SESSION_COOKIE_SAMESITE = "Lax"
X_FRAME_OPTIONS = "DENY"
SECURE_CONTENT_TYPE_NOSNIFF = env.bool("DJANGO_SECURE_CONTENT_TYPE_NOSNIFF", default=True)

DEFAULT_HSTS_SECONDS = 365 * 24 * 60 * 60  # 1 year
SECURE_HSTS_SECONDS = int(env.int("SECURE_HSTS_SECONDS", DEFAULT_HSTS_SECONDS))

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {
            "class": "src.base.logging.DjangoJsonRequestFormatter",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "json",
            "stream": sys.stdout,
        },
    },
    "root": {
        "handlers": ["console"],
        "level": env.str("DJANGO_LOG_LEVEL", "INFO"),
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "django.request": {
            "handlers": ["console"],
            "level": "ERROR",
            "propagate": False,
        },
        "django.db.backends": {
            "handlers": ["console"],
            "level": env.str("DJANGO_LOG_BACKENDS_LEVEL", "DEBUG"),
            "propagate": False,
        },
    },
}

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"

EMAIL_HOST = env.str("EMAIL_HOST", "")
EMAIL_PORT = env.str("EMAIL_PORT", "")
EMAIL_HOST_USER = env.str("EMAIL_USER", "")
EMAIL_HOST_PASSWORD = env.str("EMAIL_PASSWORD", "")
EMAIL_USE_SSL = True
DEFAULT_FROM_EMAIL = env.str("EMAIL_FROM", "")

SECURE_CSP = {
    "default-src": [CSP.NONE],
    "script-src": [
        CSP.SELF,
        CSP.NONCE,
        "https://static.cloudflareinsights.com",
    ],
    "style-src": [CSP.SELF, CSP.UNSAFE_INLINE],
    "font-src": [CSP.SELF],
    "img-src": [
        CSP.SELF,
        "data:",
        "https://*.giphy.com",
        "https://*.tenor.com",
        "https://*.ibb.co",
        "https://static.mahmoudashraf.dev",
        "https://www.gravatar.com",
    ],
    "media-src": [
        CSP.SELF,
        "https://static.mahmoudashraf.dev",
    ],
    "connect-src": [
        CSP.SELF,
        "https://cloudflareinsights.com",
        "https://*.cloudflareinsights.com",
    ],
    "manifest-src": [CSP.SELF],
    "object-src": [CSP.NONE],
    "frame-ancestors": [CSP.SELF],
    "frame-src": [
        CSP.SELF,
        "https://*.youtube.com",
    ],
    "form-action": [
        CSP.SELF,
        "https://github.com",
        "https://accounts.google.com",
    ],
    "base-uri": [CSP.SELF],
    "upgrade-insecure-requests": True,
}

from config.settings.sentry import *  # noqa: E402, F403
