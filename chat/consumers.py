from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async

class ChatConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.user = self.scope.get("user")
        if not self.user or not self.user.is_authenticated:
            await self.close(code=4001)
            return

        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.group_name = f"chat_{self.room_name}"

        allowed = await self.is_allowed_by_group()
        if not allowed:
            await self.close(code=4003)
            return

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

        await self.send_json({"type": "connected", "room": self.room_name})

        history = await self.get_last_messages()
        
        await self.send_json({
            "type": "chat_history",
            "messages": history
        })


    async def disconnect(self):
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def ticket_closed_event(self, event):
        await self.send_json({
            "type": "ticket_closed",
            "message": event["message"]
        })
        await self.close(code=4000)

    async def room_renamed_event(self, event):
        await self.send_json({
            "type": "room_renamed",
            "new_title": event["new_title"]
        })

    async def receive_json(self, content):
        is_closed = await self.is_room_closed()
        if is_closed:
            await self.send_json({"error": "This ticket is closed and cannot be sent."})
            return

        message_text = content.get("message", "").strip()

        if not message_text:
            await self.send_json({"error": "Message text is required."})
        return
    async def chat_message(self, event):
        await self.send_json({
            "type": "message",
            
            "id": event.get("id"),
            "sender": event["sender"],
            "message": event["message"],
            "timestamp": event.get("timestamp"),
        })
    async def chat_message_event(self, event):
        await self.send_json({
            "type": "chat_message",
            **event["message_data"]
        })


    @database_sync_to_async
    def save_message_to_db(self, message_text):
       from .models import ChatRoom, Message
       room, _ = ChatRoom.objects.get_or_create(name=self.room_name)
       msg = Message.objects.create(
           room=room,
           sender=self.user,
           content=message_text
       )
       return {
           "id": msg.id,
           "timestamp": msg.timestamp.strftime("%Y-%m-%d %H:%M:%S")
       }


    @database_sync_to_async
    def is_allowed_by_group(self):
        user_groups = set(self.user.groups.values_list("name", flat=True))

        ADMIN_GROUP = "Admin"       
        SUPPORT_GROUP = "Operator"   
        CUSTOMER_GROUP = "Customer" 

        if self.user.is_superuser or ADMIN_GROUP in user_groups:
            return True

        if SUPPORT_GROUP in user_groups:
            return True

        if CUSTOMER_GROUP in user_groups:
            from .models import ChatRoom
            room = ChatRoom.objects.filter(name=self.room_name).first()
            
            if not room:
                ChatRoom.objects.create(name=self.room_name, owner=self.user)
                return True
            
            return room.owner_id == self.user.id

        return False
    @database_sync_to_async
    def get_last_messages(self):
        try:
            from .models import ChatRoom, Message
            
            room = ChatRoom.objects.filter(name=self.room_name).first()
            messages = Message.objects.filter(room=room).select_related("sender").order_by("timestamp")
            
            history_list = []
            for msg in messages:
             history_list.append({
                    "id": msg.id,
                    "sender": msg.sender.username if msg.sender else "Unknown",
                    "message": msg.content or "",
                    "file_url": msg.file.url if msg.file else None,
                    "timestamp": msg.timestamp.strftime("%Y-%m-%d %H:%M:%S") if msg.timestamp else "",
                })
            return history_list

        except Exception as e:
            print(f"--> [ERROR in get_last_messages]: {e}")
            return []
    @database_sync_to_async
    def is_room_closed(self):
        from .models import ChatRoom
        room = ChatRoom.objects.filter(name=self.room_name).first()
        return room.status == 'closed' if room else False

