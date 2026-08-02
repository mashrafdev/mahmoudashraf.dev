from django.contrib import admin

from .models import Guestbook
from .tasks import optimize_guestbook_html
from .utils import render_guestbook_markdown


@admin.register(Guestbook)
class GuestbookAdmin(admin.ModelAdmin):
    list_display = ("name", "emoji", "visibility", "style", "radius", "created_at")
    list_filter = ("visibility", "style", "radius", "created_at")
    search_fields = ("name", "message", "url")
    readonly_fields = ("created_at", "message_html")

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "name",
                    "emoji",
                    "message",
                    "message_html",
                    "url",
                    "pinned",
                )
            },
        ),
        (
            "Display Settings",
            {
                "fields": (
                    "visibility",
                    "style",
                    "radius",
                )
            },
        ),
        (
            "Timestamps",
            {
                "fields": ("created_at",),
            },
        ),
    )

    def save_model(self, request, obj, form, change):
        if "message" in form.changed_data or not obj.message_html:
            obj.message_html = render_guestbook_markdown(obj.message)
            super().save_model(request, obj, form, change)
            optimize_guestbook_html.enqueue(obj.id)
        else:
            super().save_model(request, obj, form, change)
