from django.conf import settings

from .base import BaseNotificationDriver
from notifications.models import NotificationLog

import json
import logging
import requests


logger = logging.getLogger(__name__)


class SmsDriver(BaseNotificationDriver):
    def send_notification(
        self,
        recipient: str,
        ticket_title: str,
        ticket_id: str,
        new_status: str,
    ) -> bool:

        # only send in Console
        if getattr(settings, "SMS_CONSOLE_ONLY", True):
            sms_details = {
                "mode": "SIMULATION - NO SMS SENT",
                "recipient": str(recipient),
                "ticket_id": str(ticket_id),
                "ticket_title": str(ticket_title),
                "status": str(new_status),
                "template": "ticketStatusChanged",
                "token": str(ticket_id),
                "token2": str(new_status).replace(" ", "_"),
            }

            print("\n========== SMS DEBUG ==========")
            print(json.dumps(sms_details, ensure_ascii=False, indent=2))
            print("================================\n")

            NotificationLog.objects.create(
                ticket_id=str(ticket_id),
                destination=str(recipient),
                channel="sms",
                status="failed",
                response_data=sms_details,
                error_message="Simulation only; no SMS was sent.",
            )

            return True

        api_key = getattr(settings, "KAVENEGAR_API_KEY", "")
        if not api_key:
            logger.error("KAVENEGAR_API_KEY is not configured.")
            return False

        url = (
            f"https://api.kavenegar.com/v1/"
            f"{api_key}/verify/lookup.json"
        )

        params = {
            "receptor": recipient,
            "token": ticket_id,
            "token2": new_status.replace(" ", "_"),
            "template": "ticketStatusChanged",
        }

        try:
            response = requests.post(url, data=params, timeout=10)
            response.raise_for_status()
            result = response.json()

            provider_status = result.get("return", {}).get("status")
            is_success = provider_status == 200

            NotificationLog.objects.create(
                ticket_id=ticket_id,
                recipient=recipient,
                channel="sms",
                status="sent" if is_success else "failed",
                response_data=json.dumps(
                    result, ensure_ascii=False
                ),
                error_message=(
                    None if is_success else json.dumps(
                        result, ensure_ascii=False
                    )
                ),
            )

            logger.info(
                "SMS API result: recipient=%s ticket=%s success=%s",
                recipient,
                ticket_id,
                is_success,
            )
            return is_success

        except (requests.RequestException, ValueError) as exc:
            logger.exception("SMS request failed")

            NotificationLog.objects.create(
                ticket_id=ticket_id,
                recipient=recipient,
                channel="sms",
                status="failed",
                error_message=str(exc),
            )
            return False
