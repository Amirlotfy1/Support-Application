from celery import shared_task

from .drivers.email import EmailDriver
from .drivers.sms import SmsDriver
from .drivers.bale import BaleDriver

@shared_task
def send_ticket_notification_task(ticket_id, ticket_title, new_status, email=None, phone=None, bale_chat_id=None):
    if email:
        EmailDriver().send(recipient=email, ticket_title=ticket_title, ticket_id=ticket_id, new_status=new_status)
    if phone:
        SmsDriver().send(recipient=phone, ticket_title=ticket_title, ticket_id=ticket_id, new_status=new_status)
    if bale_chat_id:
        BaleDriver().send(recipient=bale_chat_id, ticket_title=ticket_title, ticket_id=ticket_id, new_status=new_status)
