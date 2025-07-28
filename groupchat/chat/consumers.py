import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Message
from asgiref.sync import sync_to_async
from datetime import datetime, timezone

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_code = self.scope['url_route']['kwargs']['room_code']
        self.room_group_name = f'chat_{self.room_code}'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

        # Notify others that a user joined
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_notification',
                'message': 'joined the chat.',
                'username': 'System',
                'user': self.get_username()
            }
        )

        # Send last 20 messages to the connecting user
        messages = await self.get_last_messages()
        for msg in messages:
            await self.send(text_data=json.dumps({
                'username': msg.username,
                'message': msg.content,
                'timestamp': msg.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            }))

    async def disconnect(self, close_code):
        # Notify others that user left
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_notification',
                'message': 'left the chat.',
                'username': 'System',
                'user': self.get_username()
            }
        )

        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']
        username = data['username']

        # Save message to DB
        await self.save_message(self.room_code, username, message)

        # Broadcast message to group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'username': username,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
        )

    async def chat_message(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'username': event['username'],
            'timestamp': event['timestamp']
        }))

    async def chat_notification(self, event):
        # Send system notification to WebSocket
        await self.send(text_data=json.dumps({
            'message': f"{event['user']} {event['message']}",
            'username': event['username'],
            'timestamp': datetime.now(timezone.utc).isoformat()
        }))

    @sync_to_async
    def save_message(self, room_code, username, message):
        return Message.objects.create(room_code=room_code, username=username, content=message)

    @sync_to_async
    def get_last_messages(self):
        return Message.objects.filter(room_code=self.room_code).order_by('-timestamp')[:20][::-1]

    def get_username(self):
        return self.scope["user"].username if self.scope["user"].is_authenticated else "Anonymous"
