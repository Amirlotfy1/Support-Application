from django.db import models
from django.core.validators import FileExtensionValidator

from accounts.models import User

class Ticket(models.Model):
    class Status(models.TextChoices):
        send = "send" , "send"
        read = "read" , "read"
        answered = "answered" , "answered"

    class Type(models.TextChoices):
        general = "general" , "general"
        financial = "financial" , "financial"
        technical = "technical" , "technical"


    class Status_ticket(models.TextChoices):
        Open = "open" , "open"
        Following_up = "Following_up" , "Following_up"
        close = "close" , "close"


    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tickets',null=True, blank=True)
    title = models.CharField(max_length=100)
    description = models.TextField()
    file = models.FileField(upload_to='ticket_files/', null=True, blank=True ,validators=[FileExtensionValidator( ['pdf' , 'png' , 'jpg'] ) ])
    status = models.CharField(max_length=50 , choices=Status.choices , null=True, blank=True , default=Status.send)
    type = models.CharField(max_length=50 , choices=Type , blank=True , null=True)
    status_ticket = models.CharField(max_length=50 , choices=Status_ticket , null=True , blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
    

class TicketReply(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='replies')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ticket_replies')
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Reply to '{self.ticket.title}' by {self.user.username}"
