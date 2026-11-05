from django.db.models.signals import post_save
from django.dispatch import receiver

from tickets.models import Ticket 

from notifications.drivers.bale import BaleDriver
from notifications.drivers.email import EmailDriver
from notifications.drivers.sms import SmsDriver

@receiver(post_save, sender=Ticket)
def send_ticket_notification_on_save(sender, instance, created, **kwargs):
    user = getattr(instance, 'user', getattr(instance, 'created_at', None))
    if not user:
        return
    status_text = "New ticket successfully registered" if created else getattr(instance, 'get_status_display', lambda: str(instance.status))()
    ticket_title = getattr(instance, 'title', getattr(instance, 'subject', 'Untitled'))
    ticket_id = str(instance.id)

    chat_id = getattr(user, 'bale_chat_id', None)
    if not chat_id and hasattr(user, 'profile'):
        chat_id = getattr(user.profile, 'bale_chat_id', None)

    if chat_id:
        bale_driver = BaleDriver()
        bale_driver.send_notification(
            recipient=chat_id,
            ticket_id=ticket_id,
            ticket_title=ticket_title,
            new_status=status_text,
            user=user
        )

    user_email = getattr(user, 'email', None)
    if user_email:
        email_driver = EmailDriver()
        email_driver.send_notification(
            recipient=user_email,
            ticket_id=ticket_id,
            ticket_title=ticket_title,
            new_status=status_text,
            user=user
        )

    phone = getattr(user, "phone_number", None)

    if phone:
        sms_driver = SmsDriver()
        sms_driver.send_notification(
            recipient=phone,
            ticket_id=ticket_id,
            ticket_title=ticket_title,
            new_status=status_text,
        )
    