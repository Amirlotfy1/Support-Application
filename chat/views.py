from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status , viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.pagination import PageNumberPagination

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from .serializers import ChatRoomUpdateSerializer , ChatRoomSerializer
from .models import ChatRoom, Message

class ChatRoomManageView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, room_name):
        user_groups = request.user.groups.values_list('name', flat=True)

        if not (
            request.user.is_superuser
            or 'Admin' in user_groups
            or 'Support' in user_groups
        ):
            return Response(
                {"detail": "Access Denied."},
                status=status.HTTP_403_FORBIDDEN
            )

        room = ChatRoom.objects.filter(name=room_name).first()

        if not room:
            return Response(
                {"detail": "Room not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = ChatRoomUpdateSerializer(room)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, room_name):
        user_groups = request.user.groups.values_list('name', flat=True)
        if not (request.user.is_superuser or 'Admin' in user_groups or 'Support' in user_groups):
            return Response({"detail": "Access Denied."}, status=status.HTTP_403_FORBIDDEN)

        room = ChatRoom.objects.filter(name=room_name).first()
        if not room:
            return Response({"detail": "Room not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = ChatRoomUpdateSerializer(room, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()

            channel_layer = get_channel_layer()
            group_name = f"chat_{room_name}"

            if 'status' in serializer.validated_data and serializer.validated_data['status'] == 'closed':
                async_to_sync(channel_layer.group_send)(
                    group_name,
                    {
                        "type": "ticket_closed_event",
                        "message": "This ticket has been closed by support."
                    }
                )

            if 'title' in serializer.validated_data:
                async_to_sync(channel_layer.group_send)(
                    group_name,
                    {
                        "type": "room_renamed_event",
                        "new_title": serializer.validated_data['title']
                    }
                )

            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




class MessagePagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 1


class File_UploadMessageView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request, room_name):
        room = ChatRoom.objects.filter(name=room_name).first()

        if not room:
            return Response(
                {"detail": "اتاق چت یافت نشد."},
                status=status.HTTP_404_NOT_FOUND
            )

        user_groups = request.user.groups.values_list(
            'name', flat=True
        )

        is_staff = (
            request.user.is_superuser
            or 'Admin' in user_groups
            or 'Support' in user_groups
        )

        if not is_staff and room.owner_id != request.user.id:
            return Response(
                {"detail": "دسترسی غیرمجاز."},
                status=status.HTTP_403_FORBIDDEN
            )

        # Optimize: load each sender in the same SQL query.
        messages = (
            Message.objects
            .filter(room_id=room.id)
            .select_related('sender')
            .order_by('timestamp', 'id')
        )

        # Return a limited page of messages.
        paginator = MessagePagination()
        page = paginator.paginate_queryset(messages, request, view=self)

        data = [
            {
                "id": msg.id,
                "sender": msg.sender.username,
                "message": msg.content,
                "file_url": (
                    request.build_absolute_uri(msg.file.url)
                    if msg.file else None
                ),
                "file_name": (
                    msg.file.name.split('/')[-1]
                    if msg.file else None
                ),
                "timestamp": msg.timestamp.strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
            }
            for msg in page
        ]

        return paginator.get_paginated_response(data)


    def post(self, request, room_name):
        room = ChatRoom.objects.filter(name=room_name).first()
        if not room:
            return Response({"detail": "Chat room not found."}, status=status.HTTP_404_NOT_FOUND)

        if room.status == 'closed':
            return Response({"detail": "The ticket is closed and the file cannot be sent."}, status=status.HTTP_400_BAD_REQUEST)

        user_groups = request.user.groups.values_list('name', flat=True)
        is_staff = request.user.is_superuser or 'Admin' in user_groups or 'Support' in user_groups
        if not is_staff and room.owner != request.user:
            return Response({"detail": "Access Denied."}, status=status.HTTP_403_FORBIDDEN)

        file_obj = request.FILES.get('file')
        if not file_obj:
            return Response({"detail": "File not sent."}, status=status.HTTP_400_BAD_REQUEST)

        content_text = request.data.get('content', '')

        msg = Message.objects.create(
            room=room,
            sender=request.user,
            content=content_text,
            file=file_obj
        )

        file_url = request.build_absolute_uri(msg.file.url)

        message_data = {
            "id": msg.id,
            "sender": msg.sender.username,
            "message": msg.content,
            "file_url": file_url,
            "file_name": file_obj.name,
            "timestamp": msg.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        }

        channel_layer = get_channel_layer()
        group_name = f"chat_{room_name}"
        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                "type": "chat_message_event",
                "message_data": message_data
            }
        )

        return Response(message_data, status=status.HTTP_201_CREATED)




class chatroomviewset(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    queryset = ChatRoom.objects.all()
    serializer_class = ChatRoomSerializer

