from django.db.models import Count , Q

from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.views import APIView , Response
from rest_framework.generics import ListAPIView

from .models import Ticket
from .serializers import TicketSerializer, TicketReplySerializer
from .permissions import is_admin_or_operator
from . import serializers

@api_view(['GET', 'POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def ticket_list(request):
    if request.method == 'GET':
        if is_admin_or_operator(request.user):
            tickets = Ticket.objects.all()
        else:
            tickets = Ticket.objects.filter(user=request.user)

        serializer = TicketSerializer(tickets, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = TicketSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PATCH'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def ticket_detail(request, pk):
    try:
        ticket = Ticket.objects.get(pk=pk)
    except Ticket.DoesNotExist:
        return Response({'error': 'Ticket not found'}, status=status.HTTP_404_NOT_FOUND)

    if ticket.user != request.user and not is_admin_or_operator(request.user):
        return Response({'error': 'دسترسی غیرمجاز'}, status=status.HTTP_403_FORBIDDEN)

    if request.method == 'GET':
        if is_admin_or_operator(request.user) and ticket.status == Ticket.Status.send:
            ticket.status = Ticket.Status.read
            ticket.save()

        serializer = TicketSerializer(ticket)
        return Response(serializer.data)

    elif request.method == 'PATCH':
        serializer = TicketSerializer(ticket, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def ticket_replies(request, ticket_id):
    try:
        ticket = Ticket.objects.get(id=ticket_id)
    except Ticket.DoesNotExist:
        return Response({'error': 'Ticket not found'}, status=status.HTTP_404_NOT_FOUND)

    if ticket.user != request.user and not is_admin_or_operator(request.user):
        return Response({'error': 'دسترسی غیرمجاز'}, status=status.HTTP_403_FORBIDDEN)

    if request.method == 'GET':
        replies = ticket.replies.all()
        serializer = TicketReplySerializer(replies, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = TicketReplySerializer(
            data=request.data,
            context={'request': request, 'ticket_id': ticket.id}
        )
        if serializer.is_valid():
            reply = serializer.save()

            if is_admin_or_operator(request.user):
                ticket.status = Ticket.Status.answered
            else:
                ticket.status = Ticket.Status.send
            ticket.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class Count_ticket(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        counts = Ticket.objects.filter(
            user=request.user
        ).aggregate(
            open=Count('id', filter=Q(status_ticket='open')),
            following_up=Count(
                'id', filter=Q(status_ticket='Following_up')
            ),
            close=Count('id', filter=Q(status_ticket='close')),
        )

        return Response(counts)

class TicketListView(ListAPIView):
    serializer_class = serializers.TicketSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return (
            Ticket.objects
            .prefetch_related("replies")
            .order_by("-created_at")
        )



@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def filter_type_ticket(request):
    ticket_type = request.query_params.get('type')

    tickets = Ticket.objects.all()

    if ticket_type:
        tickets = Ticket.objects.filter(type = ticket_type)

    serializer = TicketSerializer(tickets, many=True)
    return Response(serializer.data)