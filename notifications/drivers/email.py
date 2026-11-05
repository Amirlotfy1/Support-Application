from django.core.mail import send_mail
from django.conf import settings

from notifications.drivers.base import BaseNotificationDriver
from notifications.models import NotificationLog

class EmailDriver(BaseNotificationDriver):
    def send_notification(self, recipient, ticket_id, ticket_title, new_status, user=None, **kwargs):
        """
        recipient: آدرس ایمیل کاربر (مثلاً 'user@example.com')
        user: آبجکت کاربر جنگو (اختیاری)
        """
        subject = f"🔔 به‌روزرسانی وضعیت تیکت #{ticket_id}: {ticket_title}"
        message = (
            f"کاربر گرامی،\n\n"
            f"وضعیت تیکت شما با شناسه #{ticket_id} و عنوان «{ticket_title}» تغییر کرد.\n"
            f"وضعیت جدید: {new_status}\n\n"
            f"جهت پیگیری بیشتر به سامانه پشتیبانی مراجعه فرمایید.\n"
            f"با احترام، تیم پشتیبانی"
        )
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL')
        recipient_list = [recipient]

        def log_to_db(status, err=None):
            try:
                field_names = [f.name for f in NotificationLog._meta.get_fields()]
                data = {
                    "ticket_id": str(ticket_id),
                    "channel": "email",
                    "status": status,
                }
                if "user" in field_names and user is not None:
                    data["user"] = user
                elif "recipient" in field_names and user is not None:
                    data["recipient"] = user

                if "destination" in field_names:
                    data["destination"] = recipient
                if err and "error_message" in field_names:
                    data["error_message"] = str(err)

                NotificationLog.objects.create(**data)
            except Exception as log_err:
                print(f"[Email NotificationLog Error]: {log_err}")

        try:
            sent_count = send_mail(
                subject=subject,
                message=message,
                from_email=from_email,
                recipient_list=recipient_list,
                fail_silently=False,
            )
            is_success = sent_count > 0
            log_to_db(status="sent" if is_success else "failed")
            return is_success

        except Exception as e:
            log_to_db(status="failed", err=str(e))
            return False
