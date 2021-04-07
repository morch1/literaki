from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/(?P<game_token>\w+)/$', consumers.GameConsumer.as_asgi()),
    re_path(r'ws-priv/(?P<game_player_token>\w+)/$', consumers.GamePlayerConsumer.as_asgi()),
]
