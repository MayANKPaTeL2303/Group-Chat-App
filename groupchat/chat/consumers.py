import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Message, Room
from asgiref.sync import sync_to_async
from datetime import datetime, timezone
from urllib.parse import parse_qs

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_code = self.scope['url_route']['kwargs']['room_code']
        self.room_group_name = f'chat_{self.room_code}'

        # Extract the username from the query string
        query_string = self.scope['query_string'].decode()
        query_params = parse_qs(query_string)
        self.username = query_params.get('username', ['Anonymous'])[0]

        # Check if room exists
        if not await self.room_exists():
            await self.close()
            return

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
                'message': f"{self.username} joined the chat.",
                'username': 'System',
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
                'message': f"{self.username} left the chat.",
                'username': 'System',
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
            'message': event['message'],
            'username': event['username'],
            'timestamp': datetime.now(timezone.utc).isoformat()
        }))

    @sync_to_async
    def save_message(self, room_code, username, message):
        room = Room.objects.get(code=room_code)
        return Message.objects.create(room=room, username=username, content=message)

    @sync_to_async
    def get_last_messages(self):
        return Message.objects.filter(room__code=self.room_code).order_by('-timestamp')[:20][::-1]

    @sync_to_async
    def room_exists(self):
        return Room.objects.filter(code=self.room_code).exists()