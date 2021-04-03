from literaki.settings import MAX_PLAYERS
from django.http.response import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.core.exceptions import PermissionDenied
from .models import Game, Player, PlayerInGame


def index(request):
    return render(request, 'literakiapp/index.html')


def create_game(request):
    game = Game.objects.create()
    return redirect('literakiapp:game', game_token=game.token)


def game(request, game_token):
    try:
        game = Game.objects.get(token=game_token)
    except Game.DoesNotExist:
        raise Http404('pokój nie istnieje')

    game_player = PlayerInGame.objects.filter(game=game, player=request.player).first()

    if not game.started:
        if not game_player:
            if game.playeringame_set.count() < MAX_PLAYERS:
                game_player = PlayerInGame.objects.create(game=game, player=request.player)
                # TODO: send updated player list to connected players (with info who's ready)
            else:
                raise PermissionDenied('pokój jest pełny')
        return render(request, 'literakiapp/lobby.html')
    else:
        if not game_player:
            raise PermissionDenied('gra już się rozpoczęła')
        board = [
            [5, 0, 0, 0, 0, 0, 0, 5, 0, 0, 0, 0, 0, 0, 5],
            [0, 4, 0, 0, 0, 3, 0, 0, 0, 3, 0, 0, 0, 4, 0],
            [0, 0, 4, 0, 0, 0, 2, 0, 2, 0, 0, 0, 4, 0, 0],
            [0, 0, 0, 4, 0, 0, 0, 2, 0, 0, 0, 4, 0, 0, 0],
            [0, 0, 0, 0, 4, 0, 0, 0, 0, 0, 4, 0, 0, 0, 0],
            [0, 3, 0, 0, 0, 3, 0, 0, 0, 3, 0, 0, 0, 3, 0],
            [0, 0, 2, 0, 0, 0, 2, 0, 2, 0, 0, 0, 2, 0, 0],
            [5, 0, 0, 2, 0, 0, 0, 1, 0, 0, 0, 2, 0, 0, 5],
            [0, 0, 2, 0, 0, 0, 2, 0, 2, 0, 0, 0, 2, 0, 0],
            [0, 3, 0, 0, 0, 3, 0, 0, 0, 3, 0, 0, 0, 3, 0],
            [0, 0, 0, 0, 4, 0, 0, 0, 0, 0, 4, 0, 0, 0, 0],
            [0, 0, 0, 4, 0, 0, 0, 2, 0, 0, 0, 4, 0, 0, 0],
            [0, 0, 4, 0, 0, 0, 2, 0, 2, 0, 0, 0, 4, 0, 0],
            [0, 4, 0, 0, 0, 3, 0, 0, 0, 3, 0, 0, 0, 4, 0],
            [5, 0, 0, 0, 0, 0, 0, 5, 0, 0, 0, 0, 0, 0, 5],
        ]
        context = {
            'board': board,
        }
        return render(request, 'literakiapp/game.html', context)


def error(request, exception):
    context = {'msg': str(exception)}
    return render(request, 'literakiapp/error.html', context)
