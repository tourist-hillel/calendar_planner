from django.urls import re_path
from events import consumers

websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<room_name>\w+)/$', consumers.CalendarChatConsumer.as_asgi()),
]