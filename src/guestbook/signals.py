from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Guestbook
from .tasks import send_new_entry_email


@receiver(post_save, sender=Guestbook)
def notify_new_guestbook_entry(sender, instance, created, **kwargs):
    if created:
        send_new_entry_email.enqueue(instance.id)  # type: ignore
