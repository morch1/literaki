from django.contrib import admin
from .models import Game, LetterOnBoard, Player, PlayerInGame

admin.site.register(Game)
admin.site.register(Player)
admin.site.register(PlayerInGame)
admin.site.register(LetterOnBoard)
