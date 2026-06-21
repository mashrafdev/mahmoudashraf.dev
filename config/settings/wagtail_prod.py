from config.env import env

WAGTAILFRONTENDCACHE = {
    "cloudflare": {
        "BACKEND": "wagtail.contrib.frontend_cache.backends.CloudflareBackend",
        "EMAIL": env.str("CLOUDFLARE_EMAIL", ""),
        "API_KEY": env.str("CLOUDFLARE_API_KEY", ""),
        "ZONEID": env.str("CLOUDFLARE_ZONEID", ""),
    },
}

WAGTAILADMIN_BASE_URL = "https://mahmoudashraf.dev"
