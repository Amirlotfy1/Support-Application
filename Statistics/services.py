from django.db.models import OuterRef, Subquery, F, Avg, DurationField, ExpressionWrapper

from tickets.models import Ticket, TicketReply
from chat.models import Message

from datetime import timedelta

from .utils import get_current_month_range

class OperatorStatisticsService:
    @classmethod
    def get_monthly_report(cls, operator, ticket_type=None, use_jalali=False):
        start_date, end_date = get_current_month_range(use_jalali=use_jalali)

        replies_qs = TicketReply.objects.filter(
            user=operator,
            created_at__gte=start_date,
            created_at__lte=end_date
        )

        ticket_ids_handled = replies_qs.values_list('ticket_id', flat=True).distinct()
        tickets_qs = Ticket.objects.filter(id__in=ticket_ids_handled)

        if ticket_type:
            tickets_qs = tickets_qs.filter(ticket_type=ticket_type)
            ticket_ids_handled = tickets_qs.values_list('id', flat=True)

        ticket_customer_ids = set(
            tickets_qs.exclude(user__isnull=True)
            .values_list('user_id', flat=True)
            .distinct()
        )

        first_reply_subquery = TicketReply.objects.filter(
            ticket=OuterRef('pk'),
            user=operator
        ).order_by('created_at').values('created_at')[:1]

        annotated_tickets = tickets_qs.annotate(
            first_reply_time=Subquery(first_reply_subquery)
        ).filter(first_reply_time__isnull=False).annotate(
            response_duration=ExpressionWrapper(
                F('first_reply_time') - F('created_at'),
                output_field=DurationField()
            )
        )

        avg_duration_dict = annotated_tickets.aggregate(avg_time=Avg('response_duration'))
        avg_duration = avg_duration_dict.get('avg_time')

        avg_response_minutes = 0.0
        if avg_duration and isinstance(avg_duration, timedelta):
            avg_response_minutes = round(avg_duration.total_seconds() / 60, 2)

        messages_qs = Message.objects.filter(
            sender=operator,
            timestamp__gte=start_date,
            timestamp__lte=end_date
        )

        handled_rooms_count = messages_qs.values('room_id').distinct().count()

        chat_customer_ids = set(
            messages_qs.exclude(room__owner__isnull=True)
            .values_list('room__owner_id', flat=True)
            .distinct()
        )

        total_unique_customers_count = len(ticket_customer_ids.union(chat_customer_ids))
        return {
            "period": {
                "start": start_date,
                "end": end_date,
            },
            "operator": {
                "id": operator.id,
                "username": operator.username,
                "email": operator.email
            },
            "tickets": {
                "handled_count": tickets_qs.count(),
                "unique_customers_count": len(ticket_customer_ids),
                "avg_response_time_minutes": avg_response_minutes,
                "applied_ticket_type_filter": ticket_type,
            },
            "chats": {
                "handled_rooms_count": handled_rooms_count,
                "unique_customers_count": len(chat_customer_ids),
            },
            "overall_unique_customers_handled": total_unique_customers_count
        }
