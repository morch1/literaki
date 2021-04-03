import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import JsonWebsocketConsumer

class GameConsumer(JsonWebsocketConsumer):
    def connect(self):
        self.game_token = self.scope['url_route']['kwargs']['game_token']
        async_to_sync(self.channel_layer.group_add)(self.game_token, self.channel_name)
        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(self.game_token, self.channel_name)

    def receive_json(self, content):
        pass

    def message(self, event):
        data = dict((k, v) for k, v in event.items() if k!= 'type')
        print(data)
        self.send_json(data)
