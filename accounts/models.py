from django.db import models
from django.contrib.auth.models import AbstractUser
from phonenumber_field.modelfields import PhoneNumberField

class User(AbstractUser):
    email = models.EmailField(unique=True , max_length=254)
    bale_chat_id = models.CharField(max_length=50 , null=True , blank=True)
    phone_number = PhoneNumberField(null=True, blank=True, unique=True)
    REQUIRED_FIELDS = ['email']

    class Meta:
        pass

    def __str__(self):
        return self.username