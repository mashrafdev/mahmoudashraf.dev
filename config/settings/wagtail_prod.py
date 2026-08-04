from config.env import env

WAGTAILFRONTENDCACHE = {
    "cloudflare": {
        "BACKEND": "wagtail.contrib.frontend_cache.backends.CloudflareBackend",
        "ZONEID": env.str("CLOUDFLARE_ZONEID", ""),
        "BEARER_TOKEN": env.str("CLOUDFLARE_CACHE_TOKEN", ""),
    },
}

WAGTAILADMIN_BASE_URL = "https://mahmoudashraf.dev"
