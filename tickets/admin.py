
from django.contrib import admin

from .models import Ticket, TicketReply


@admin.register(TicketReply)
class TicketReplyAdmin(admin.ModelAdmin):
    list_select_related = ("ticket", "user")


admin.site.register(Ticket)
