import random
from literaki.settings import MAX_PLAYERS
from django.http.response import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.core.exceptions import PermissionDenied
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Game, PlayerInGame


def _send_update(game_token, msg_type, data=None):
    channel_layer = get_channel_layer()
    data_to_send = data or {}
    data_to_send['type'] = 'message'
    data_to_send['msg_type'] = msg_type
    async_to_sync(channel_layer.group_send)(game_token, data_to_send)


def index(request):
    return render(request, 'literakiapp/index.html')


def error(request, exception):
    context = {'msg': str(exception)}
    return render(request, 'literakiapp/error.html', context)


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
                _send_update(game_token, 'player_joined', {
                    'player_id': game_player.id,
                    'player_name': game_player.player.name,
                })
            else:
                raise PermissionDenied('pokój jest pełny')
        players = game.playeringame_set.all()
        context = {
            'game_token': game_token,
            'me': game_player,
            'players': players,
        }
        return render(request, 'literakiapp/lobby.html', context)
    else:
        if not game_player:
            raise PermissionDenied('nie można dołączyć w trakcie gry')
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
        players = game.playeringame_set.order_by('-score')
        current_player = game.playeringame_set.order_by('-order').first()
        context = {
            'me': game_player,
            'players': players,
            'current_player': current_player,
            'game_token': game_token,
            'board': board,
        }
        return render(request, 'literakiapp/game.html', context)


def change_name(request, game_token):
    print(request.player)
    game = get_object_or_404(Game, token=game_token)
    game_player = get_object_or_404(PlayerInGame, game=game, player=request.player)
    request.player.name = request.POST['new_name']
    request.player.save()
    _send_update(game_token, 'player_name_changed', {
        'player_id': game_player.id,
        'new_name': request.player.name,
    })
    return HttpResponse()


def _check_start(game):
    players = game.playeringame_set.order_by('?')
    if players.count() > 1 and all(p.ready for p in players):
        for i, p in enumerate(players):
            p.order = i
            p.letters = game.letters[:7]
            p.save()
            game.letters = game.letters[7:]
        game.started = True
        game.save()
        _send_update(game.token, 'game_started')


def ready(request, game_token):
    game = get_object_or_404(Game, token=game_token)
    game_player = get_object_or_404(PlayerInGame, game=game, player=request.player)
    if not game_player.ready:
        game_player.ready = True
        game_player.save()
        _send_update(game_token, 'player_ready', {
            'player_id': game_player.id,
        })
        _check_start(game)
    return HttpResponse()


def leave(request, game_token):
    game = get_object_or_404(Game, token=game_token)
    game_player = get_object_or_404(PlayerInGame, game=game, player=request.player)
    letters = list(game.letters + game_player.letters)
    random.shuffle(letters)
    game.letters = ''.join(letters)
    if game.started:
        # TODO: co jesli jest teraz ruch tego gracza?
        pass
    game.save()
    _send_update(game_token, 'player_left', {
        'player_id': game_player.id,
    })
    game_player.delete()
    _check_start(game)
    return redirect('literakiapp:index')
