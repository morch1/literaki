import uuid
import random
from django.db import models

def randid():
    return str(uuid.uuid4().hex)


def randname():
    return randid()[:7]


def randletters():
    letters = list('a' * 9 + 'ą' + 'b' * 2 + 'c' * 3 + 'ć' + 'd' * 3 + 'e' * 7 + 'ę' * 1 + 'f' * 1 + 'g' * 2 + 'h' * 2 + 'i' * 8 + 'j' * 2 + 'k' * 3 + 'l' * 3 + 'ł' * 2 + 'm' * 3 + 'n' * 5 + 'ń' + 'o' * 6 + 'ó' + 'p' * 3 + 'r' * 4 + 's' * 4 + 'ś' + 't' * 3 + 'u' * 2 + 'w' * 4 + 'y' * 4 + 'z' * 5 + 'ź' + 'ż' + ' ' * 2)
    random.shuffle(letters)
    return ''.join(letters)


class Player(models.Model):
    token = models.CharField(max_length=32, default=randid, unique=True)
    name = models.CharField(max_length=32, default=randname)

    def __str__(self) -> str:
        return f'{self.name} ({self.token})'


class Game(models.Model):
    token = models.CharField(max_length=32, default=randid, unique=True)
    started = models.BooleanField(default=False)
    letters = models.CharField(max_length=100, default=randletters)

    def __str__(self) -> str:
        return self.token


class PlayerInGame(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    letters = models.CharField(max_length=7, blank=True, default='')
    order = models.IntegerField(default=-1)
    ready = models.BooleanField(default=False)
    score = models.IntegerField(default=0)

    class Meta:
        unique_together = ['game', 'player']

    def __str__(self) -> str:
        return f'{self.game} / {self.player.name}'


class LetterOnBoard(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    accepted = models.BooleanField(default=False)
    x = models.IntegerField()
    y = models.IntegerField()
    letter = models.CharField(max_length=1)

    class Meta:
        unique_together = ['game', 'x', 'y']

    def __str__(self) -> str:
        return f'{self.game}: {self.letter} @ ({self.x}, {self.y})'
