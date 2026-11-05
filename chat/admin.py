from django.contrib import admin

from .models import ChatRoom, Message

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_select_related = ("sender",)

admin.site.register(ChatRoom)