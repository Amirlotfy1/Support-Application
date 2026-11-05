from django.conf import settings

from notifications.drivers.base import BaseNotificationDriver
from notifications.models import NotificationLog

import requests


class BaleDriver(BaseNotificationDriver):
    def __init__(self):
        self.token = getattr(settings, 'BALE_BOT_TOKEN', '')
        self.api_url = f"https://tapi.bale.ai/bot{self.token}/sendMessage"

    def send_notification(self, recipient, ticket_id, ticket_title, new_status, user=None, **kwargs):
        chat_id = str(recipient)

        message_text = (
            f"🔔 وضعیت تیکت شما به شرح زیر می باشد:\n\n"
            f"شماره تیکت: #{ticket_id}\n"
            f"عنوان: {ticket_title}\n"
            f"وضعیت: {new_status}\n\n"
            f" سامانه پشتیبانی توزیکو"
        )

        payload = {
            "chat_id": chat_id,
            "text": message_text
        }

        def log_to_db(status, res_data=None, err=None):
            try:
                field_names = [f.name for f in NotificationLog._meta.get_fields()]
                data = {
                    "ticket_id": str(ticket_id),
                    "channel": "bale",
                    "status": status,
                }
                
                if "user" in field_names and user is not None:
                    data["user"] = user
                elif "recipient" in field_names and user is not None:
                    data["recipient"] = user

                if "destination" in field_names:
                    data["destination"] = chat_id

                if res_data and "response_data" in field_names:
                    data["response_data"] = res_data
                if err and "error_message" in field_names:
                    data["error_message"] = str(err)

                NotificationLog.objects.create(**data)
            except Exception as log_err:
                print(f"[NotificationLog Error]: {log_err}")

        try:
            response = requests.post(self.api_url, json=payload, timeout=10)
            res_data = response.json()
            is_success = (response.status_code == 200 and res_data.get("ok") is True)

            log_to_db(
                status="sent" if is_success else "failed",
                res_data=res_data,
                err=None if is_success else res_data.get("description")
            )
            return is_success

        except Exception as e:
            log_to_db(status="failed", err=str(e))
            return False
