from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import FileExtensionValidator

User = get_user_model()

class ChatRoom(models.Model):
    STATUS_CHOICES = (
        ('open', 'Open'),
        ('closed', 'Closed'),
    )

    name = models.CharField(max_length=100, unique=True) 
    title = models.CharField(max_length=255, blank=True, null=True) 
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_rooms', null=True, blank=True) 
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='open')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.status}"

class Message(models.Model):
    room = models.ForeignKey('ChatRoom', on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_messages')
    content = models.TextField(blank=True, null=True)
    file = models.FileField(upload_to='chat_attachments/%Y/%m/%d/', blank=True, null=True ,validators=[FileExtensionValidator( ['pdf' , 'jpg' , 'png'] ) ])
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.username}: {self.content or 'File attachment'}"
