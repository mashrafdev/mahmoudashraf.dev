from debug_toolbar.toolbar import debug_toolbar_urls
from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView
from health_check.views import HealthCheckView
from wagtail import urls as wagtail_urls
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.contrib.sitemaps.views import sitemap
from wagtail.documents import urls as wagtaildocs_urls

from src.base import views
from src.search.views import SearchView

urlpatterns = debug_toolbar_urls() + [
    path(
        "ht/container/",
        HealthCheckView.as_view(
            checks=[
                "health_check.Database",
                "health_check.Cache",
            ]
        ),
        name="health_check-container",
    ),
    path(settings.DJANGO_ADMIN_PATH, admin.site.urls),
    path("forms/contact/", include("src.contact.urls")),
    path("forms/guestbook/", include("src.guestbook.urls")),
    path("captcha/", include("captcha.urls")),
    path("search/", SearchView.as_view(), name="search"),
    path(settings.WAGTAIL_ADMIN_PATH, include(wagtailadmin_urls)),
    path("comments/", include("src.comments.urls")),
    path("rss/", include("src.feeds.urls")),
    path("accounts/", include("src.accounts.urls")),
    path("robots.txt/", views.robots_txt),
    path("documents/", include(wagtaildocs_urls)),
    path("sitemap.xml/", sitemap),
]

if settings.DEBUG:
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += [
        path(
            "favicon.ico",
            RedirectView.as_view(url=settings.STATIC_URL + "favicon.ico"),
        )
    ]

    urlpatterns += [
        path("test404/", views.error_404_view),
        path("test500/", views.error_500_view),
    ]

urlpatterns += [
    path("", include(wagtail_urls)),
]

handler404 = "src.base.views.error_404_view"
handler500 = "src.base.views.error_500_view"
