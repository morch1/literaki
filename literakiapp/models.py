import uuid
import random
from django.db import models

def randid():
    return str(uuid.uuid4().hex)


def randname():
    return randid()[:7]


def randletters():
    letters = list('A' * 9 + 'Ą' + 'B' * 2 + 'C' * 3 + 'Ć' + 'D' * 3 + 'E' * 7 + 'Ę' * 1 + 'F' * 1 + 'G' * 2 + 'H' * 2 + 'I' * 8 + 'J' * 2 + 'K' * 3 + 'L' * 3 + 'Ł' * 2 + 'M' * 3 + 'N' * 5 + 'Ń' + 'O' * 6 + 'Ó' + 'P' * 3 + 'R' * 4 + 'S' * 4 + 'Ś' + 'T' * 3 + 'U' * 2 + 'W' * 4 + 'Y' * 4 + 'Z' * 5 + 'Ź' + 'Ż' + ' ' * 2)
    random.shuffle(letters)
    return ''.join(letters)


class Player(models.Model):
    token = models.CharField(max_length=32, default=randid, unique=True)
    name = models.CharField(max_length=32, default=randname)

    def __str__(self) -> str:
        return f'{self.name} ({self.token})'


FIELD_LETTER_X2 = 2
FIELD_LETTER_X3 = 3
FIELD_WORD_X2 = 4
FIELD_WORD_X3 = 5

BOARD_LAYOUT = [
    [5, 0, 0, 0, 0, 0, 0, 5, 0, 0, 0, 0, 0, 0, 5],
    [0, 4, 0, 0, 0, 3, 0, 0, 0, 3, 0, 0, 0, 4, 0],
    [0, 0, 4, 0, 0, 0, 2, 0, 2, 0, 0, 0, 4, 0, 0],
    [0, 0, 0, 4, 0, 0, 0, 2, 0, 0, 0, 4, 0, 0, 0],
    [0, 0, 0, 0, 4, 0, 0, 0, 0, 0, 4, 0, 0, 0, 0],
    [0, 3, 0, 0, 0, 3, 0, 0, 0, 3, 0, 0, 0, 3, 0],
    [0, 0, 2, 0, 0, 0, 2, 0, 2, 0, 0, 0, 2, 0, 0],
    [5, 0, 0, 2, 0, 0, 0, 4, 0, 0, 0, 2, 0, 0, 5],
    [0, 0, 2, 0, 0, 0, 2, 0, 2, 0, 0, 0, 2, 0, 0],
    [0, 3, 0, 0, 0, 3, 0, 0, 0, 3, 0, 0, 0, 3, 0],
    [0, 0, 0, 0, 4, 0, 0, 0, 0, 0, 4, 0, 0, 0, 0],
    [0, 0, 0, 4, 0, 0, 0, 2, 0, 0, 0, 4, 0, 0, 0],
    [0, 0, 4, 0, 0, 0, 2, 0, 2, 0, 0, 0, 4, 0, 0],
    [0, 4, 0, 0, 0, 3, 0, 0, 0, 3, 0, 0, 0, 4, 0],
    [5, 0, 0, 0, 0, 0, 0, 5, 0, 0, 0, 0, 0, 0, 5],
]

LETTER_POINTS = {
    'A': 1, 'Ą': 5, 'B': 3, 'C': 2, 'Ć': 6, 'D': 2, 'E': 1, 'Ę': 5,
    'F': 5, 'G': 3, 'H': 3, 'I': 1, 'J': 3, 'K': 2, 'L': 2, 'Ł': 3,
    'M': 2, 'N': 1, 'Ń': 7, 'O': 1, 'Ó': 5, 'P': 2, 'R': 1, 'S': 1,
    'Ś': 5, 'T': 2, 'U': 3, 'W': 1, 'Y': 2, 'Z': 1, 'Ź': 9, 'Ż': 5,
    ' ': 0,
}

class Game(models.Model):
    token = models.CharField(max_length=32, default=randid, unique=True)
    started = models.BooleanField(default=False)
    letters = models.CharField(max_length=100, default=randletters)
    voting = models.BooleanField(default=False)
    current_player = models.ForeignKey('PlayerInGame', on_delete=models.SET_NULL, null=True, default=None, related_name='current_in_game')

    def get_current_player(self):
        self.current_player.refresh_from_db()
        return self.current_player

    def __str__(self) -> str:
        return self.token


class PlayerInGame(models.Model):
    token = models.CharField(max_length=32, default=randid)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    letters = models.CharField(max_length=7, blank=True, default='')
    order = models.IntegerField(default=-1)
    ready = models.BooleanField(default=False)
    score = models.IntegerField(default=0)
    left = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    vote = models.BooleanField(null=True, default=None)

    class Meta:
        unique_together = ['game', 'player']

    def __str__(self) -> str:
        return f'{self.game} / {self.player.name}'


class LetterOnBoard(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    player = models.ForeignKey(PlayerInGame, on_delete=models.CASCADE)
    accepted = models.BooleanField(default=False)
    x = models.IntegerField()
    y = models.IntegerField()
    letter = models.CharField(max_length=1)

    class Meta:
        unique_together = ['game', 'x', 'y']

    def __str__(self) -> str:
        return f'{self.game}: {self.letter} @ ({self.x}, {self.y})'
