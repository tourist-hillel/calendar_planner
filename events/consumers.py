import json
from channels.generic.websocket import AsyncWebsocketConsumer

class CalendarChatConsumer(AsyncWebsocketConsumer):
    async def connect(self) -> None:
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, code: int) -> None:
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data: str | None = None) -> None:
        text_data_json = json.loads(text_data)
        message = text_data_json.get('message', '')
        if not message:
            await self.send(text_data=json.dumps({
                'error': 'Invalid message'
            }))
        else:
            user = self.scope['user']
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'username': user.email
                }
            )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'username': event['username']
        }))