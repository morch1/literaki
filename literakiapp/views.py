import enum
import random
import json
from literaki.settings import MAX_PLAYERS
from django.http.response import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.core.exceptions import PermissionDenied
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Game, LetterOnBoard, PlayerInGame


def _broadcast_update(game_token, msg_type, data=None):
    channel_layer = get_channel_layer()
    data_to_send = data or {}
    data_to_send['type'] = 'message'
    data_to_send['msg_type'] = msg_type
    async_to_sync(channel_layer.group_send)(game_token, data_to_send)

def _send_update(game_player_token, msg_type, data=None):
    channel_layer = get_channel_layer()
    data_to_send = data or {}
    data_to_send['type'] = 'message'
    data_to_send['msg_type'] = msg_type
    async_to_sync(channel_layer.group_send)(f'priv-{game_player_token}', data_to_send)


def index(request):
    return render(request, 'literakiapp/index.html')


def error(request, exception):
    context = {'msg': str(exception)}
    return render(request, 'literakiapp/error.html', context)


def create_game(request):
    game = Game.objects.create()
    PlayerInGame.objects.create(game=game, player=request.player, is_admin=True)
    return redirect('literakiapp:game', game_token=game.token)


def game(request, game_token):
    try:
        game = Game.objects.get(token=game_token)
    except Game.DoesNotExist:
        raise Http404('pokój nie istnieje')

    game_player = PlayerInGame.objects.filter(game=game, player=request.player, left=False).first()

    if not game.started:
        if not game_player:
            if game.playeringame_set.count() < MAX_PLAYERS:
                game_player = PlayerInGame.objects.create(game=game, player=request.player)
                _broadcast_update(game_token, 'player_joined', {
                    'player_id': game_player.id,
                    'player_name': game_player.player.name,
                })
            else:
                raise PermissionDenied('pokój jest pełny')
        players = game.playeringame_set.all()
        context = {
            'game': game,
            'me': game_player,
            'players': players,
        }
        return render(request, 'literakiapp/lobby.html', context)
    else:
        if not game_player:
            raise PermissionDenied('nie można dołączyć w trakcie gry')
        board_layout = [
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
        board = []
        for y, row in enumerate(board_layout):
            r = []
            for x, field in enumerate(row):
                r.append((field, game.letteronboard_set.filter(x=x, y=y).first()))
            board.append(r)
        players = game.playeringame_set.order_by('order')
        context = {
            'game': game,
            'me': game_player,
            'players': players,
            'board': board,
        }
        return render(request, 'literakiapp/game.html', context)


def change_name(request, game_token):
    game = get_object_or_404(Game, token=game_token)
    game_player = get_object_or_404(PlayerInGame, game=game, player=request.player, left=False)
    request.player.name = request.POST['new_name']
    request.player.save()
    _broadcast_update(game_token, 'player_name_changed', {
        'player_id': game_player.id,
        'new_name': request.player.name,
    })
    return HttpResponse()


def _check_start(game):
    players = game.playeringame_set.order_by('?')
    if players.count() > 1 and all(p.ready for p in players):
        game.current_player = players.first()
        for i, p in enumerate(players):
            p.order = i
            p.letters = game.letters[:7]
            p.save()
            game.letters = game.letters[7:]
        game.started = True
        game.save()
        _broadcast_update(game.token, 'game_started')


def ready(request, game_token):
    game = get_object_or_404(Game, token=game_token, started=False)
    game_player = get_object_or_404(PlayerInGame, game=game, player=request.player)
    if not game_player.ready:
        game_player.ready = True
        game_player.save()
        _broadcast_update(game_token, 'player_ready', {
            'player_id': game_player.id,
        })
        _check_start(game)
    return HttpResponse()


def _kick_player(game_player):
    game = game_player.game
    letters = list(game.letters + game_player.letters)
    random.shuffle(letters)
    game.letters = ''.join(letters)
    game.save()
    if game.started:
        game_player.letters = ''
        game_player.left = True
        game_player.save()
        _broadcast_update(game.token, 'player_left', {
            'player_id': game_player.id,
            'letters_left': len(game.letters),
        })
        # TODO: co jesli jest teraz ruch tego gracza?
        # jeśli wyszedl w czasie glosowania - glosowanie trwa dalej
        # jesli wyszedl w czasie swojego ruchu - wybierz kolejnego gracza
        pass
    else:
        _broadcast_update(game.token, 'player_left', {
            'player_id': game_player.id,
        })
        game_player.delete()
        _check_start(game)


def leave(request, game_token):
    game = get_object_or_404(Game, token=game_token)
    game_player = get_object_or_404(PlayerInGame, game=game, player=request.player, left=False)
    _kick_player(game_player)
    return HttpResponse()


def kick_player(request, game_token):
    game = get_object_or_404(Game, token=game_token)
    game_player = get_object_or_404(PlayerInGame, game=game, player=request.player, left=False)
    if not game_player.is_admin:
        raise PermissionDenied()
    kicked_game_player = get_object_or_404(PlayerInGame, id=request.POST['player_id'], left=False)
    _kick_player(kicked_game_player)
    return HttpResponse()


def place_letters(request, game_token):
    game = get_object_or_404(Game, token=game_token)
    game_player = get_object_or_404(PlayerInGame, game=game, player=request.player, left=False)
    placed_letters = json.loads(request.POST['letters'])
    player_letters = game_player.letters
    letters_broadcast = []
    for i, [x, y] in placed_letters.items():
        letters_broadcast.append([player_letters[int(i)], int(x), int(y)])
        LetterOnBoard.objects.create(game=game, player=game_player, x=int(x), y=int(y), letter=player_letters[int(i)])
    for i in sorted(placed_letters.keys(), reverse=True):
        player_letters = player_letters[:int(i)] + player_letters[int(i)+1:]
    game_player.letters = player_letters
    game_player.save()
    _send_update(game_player.token, 'update_letters', {
        'letters': game_player.letters
    })
    for p in game.playeringame_set.all():
        p.vote = None
        p.save()
    game.voting = True
    game.save()
    _broadcast_update(game.token, 'vote_start', {
        'letters': letters_broadcast,
    })
    return HttpResponse()
