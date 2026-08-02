from bs4 import BeautifulSoup, Tag
from django_tasks import task

from src.guestbook.utils import highlight_code, optimize_img_tag


@task()
def send_new_entry_email(guestbook_id: int):
    from django.conf import settings
    from django.core.mail import send_mail

    from src.guestbook.models import Guestbook

    try:
        guestbook = Guestbook.objects.get(id=guestbook_id)
    except Guestbook.DoesNotExist:
        return

    subject = f"New Guestbook Entry: {guestbook.name}"
    message = (
        f"You have a new guestbook entry!\n\n"
        f"Name: {guestbook.name}\n"
        f"Message:\n{guestbook.message}\n"
    )

    recipient_list = [email for name, email in getattr(settings, "ADMINS", [])]
    if not recipient_list:
        recipient_list = [getattr(settings, "DEFAULT_FROM_EMAIL", "admin@localhost")]

    send_mail(
        subject=subject,
        message=message,
        from_email=getattr(settings, "DEFAULT_FROM_EMAIL", "webmaster@localhost"),
        recipient_list=recipient_list,
        fail_silently=True,
    )


@task()
def optimize_guestbook_html(guestbook_id: int):
    from src.guestbook.models import Guestbook

    try:
        guestbook = Guestbook.objects.get(id=guestbook_id)
    except Guestbook.DoesNotExist:
        return

    if not guestbook.message_html:
        return

    soup = BeautifulSoup(guestbook.message_html, "html.parser")

    for pre in soup.find_all("pre"):
        if isinstance(pre, Tag):
            highlight_code(pre)

    for img in soup.find_all("img"):
        if isinstance(img, Tag):
            optimize_img_tag(img)

    guestbook.message_html = str(soup)
    guestbook.save(update_fields=["message_html"])
