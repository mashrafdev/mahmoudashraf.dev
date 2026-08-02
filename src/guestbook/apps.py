from django.apps import AppConfig


class GuestBookConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "src.guestbook"

    def ready(self):
        import src.guestbook.signals  # noqa
