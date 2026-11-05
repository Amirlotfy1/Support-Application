from django.db import models
from django.contrib.auth import get_user_model

from tickets.models import Ticket

User = get_user_model()

class NotificationLog(models.Model):
    CHANNEL_CHOICES = (
        ('sms', 'SMS'),
        ('email', 'Email'),
        ('bale', 'Bale'),
    )
    STATUS_CHOICES = (
        ('sent', 'Sent'),
        ('failed', 'Failed'),
    )

    ticket_id = models.CharField(Ticket ,max_length=64)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    destination = models.CharField(max_length=255 , null=True, blank=True)
    
    channel = models.CharField(max_length=10, choices=CHANNEL_CHOICES)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    response_data = models.JSONField(null=True, blank=True)
    error_message = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.channel} -> {self.destination} ({self.status})"
