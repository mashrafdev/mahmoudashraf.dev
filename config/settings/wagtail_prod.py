from django.core.exceptions import ImproperlyConfigured

from config.env import env

CLOUDFLARE_ZONEID = env.str("CLOUDFLARE_ZONEID", "")
CLOUDFLARE_CACHE_TOKEN = env.str("CLOUDFLARE_CACHE_TOKEN", "")

if bool(CLOUDFLARE_ZONEID) != bool(CLOUDFLARE_CACHE_TOKEN):
    raise ImproperlyConfigured("CLOUDFLARE_ZONEID and CLOUDFLARE_CACHE_TOKEN must be set together.")

if CLOUDFLARE_ZONEID and CLOUDFLARE_CACHE_TOKEN:
    WAGTAILFRONTENDCACHE = {
        "cloudflare": {
            "BACKEND": "wagtail.contrib.frontend_cache.backends.CloudflareBackend",
            "ZONEID": CLOUDFLARE_ZONEID,
            "BEARER_TOKEN": CLOUDFLARE_CACHE_TOKEN,
        },
    }

WAGTAILADMIN_BASE_URL = env.str("WAGTAILADMIN_BASE_URL", "https://mahmoudashraf.dev")
