import enum
import random
import json
from literaki.settings import MAX_PLAYERS
from django.http.response import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.core.exceptions import PermissionDenied
from django.db.models import Max, Q
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Game, LetterOnBoard, PlayerInGame, randid, BOARD_LAYOUT, LETTER_POINTS


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
        board = []
        for y, row in enumerate(BOARD_LAYOUT):
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
            'letter_points': LETTER_POINTS,
            'render_id': randid(),
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
        if not game.voting:
            _next_player(game)
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


def _next_player(game, accept=True):
        current_player = game.get_current_player()

        if not current_player.left:
            current_player.order = game.playeringame_set.filter(left=False).order_by('-order').first().order + 1
            current_player.save()

        game.voting = False
        game.current_player = game.playeringame_set.filter(left=False).order_by('order').first()
        game.save()

        _broadcast_update(game.token, 'vote_end', {
            'next_player': game.current_player.id,
            'accept': int(accept),
            'letters_left': len(game.letters),
        })


def place_letters(request, game_token):
    game = get_object_or_404(Game, token=game_token)
    game_player = get_object_or_404(PlayerInGame, game=game, player=request.player, left=False)
    if game_player != game.get_current_player():
        return HttpResponse()
    placed_letters = json.loads(request.POST['letters'])
    if len(placed_letters) == 0:
        _next_player(game)
    else:
        # TODO: check if correct placement
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
        for p in game.playeringame_set.filter(left=False):
            p.vote = None
            p.save()
        game.voting = True
        game.save()
        _broadcast_update(game.token, 'vote_start', {
            'letters': letters_broadcast,
        })
    return HttpResponse()


def exchange_letters(request, game_token):
    game = get_object_or_404(Game, token=game_token)
    game_player = get_object_or_404(PlayerInGame, game=game, player=request.player, left=False)
    if game_player != game.get_current_player():
        return HttpResponse()

    exchanged_letters = json.loads(request.POST['letters'])
    print(exchanged_letters)
    game_letters = list(game.letters)[len(exchanged_letters):]
    player_letters = list(game_player.letters)
    for i, new_letter in zip(exchanged_letters, game.letters):
        game_letters.append(player_letters[i])
        player_letters[i] = new_letter
    game_player.letters = ''.join(player_letters)
    game_player.save()

    random.shuffle(game_letters)
    game.letters = ''.join(game_letters)
    game.save()

    _send_update(game_player.token, 'update_letters', {
        'letters': game_player.letters
    })
    _next_player(game)
    return HttpResponse()


def vote(request, game_token):
    game = get_object_or_404(Game, token=game_token)
    game_player = get_object_or_404(PlayerInGame, game=game, player=request.player, left=False)
    current_player = game.get_current_player()
    if not game.voting or game_player == current_player or game_player.vote is not None:
        return HttpResponse()
    vote = bool(int(request.POST['vote']))
    game_player.vote = vote
    game_player.save()
    n_true = 0
    n_false = 0
    n_null = 0
    for p in game.playeringame_set.filter(left=False).filter(~Q(id=current_player.id)):
        if p.vote == True:
            n_true += 1
        elif p.vote == False:
            n_false += 1
        else:
            n_null += 1
    
    if n_null == 0:
        letters = game.letteronboard_set.filter(accepted=False)
        
        if n_true >= n_false:
            for letter in letters:
                letter.accepted = True
                letter.save()
            if not current_player.left:
                current_player.letters += game.letters[:len(letters)]
                game.letters = game.letters[len(letters):]
            # TODO: give player points
        else:
            for letter in letters:
                if current_player.left:
                    game.letters += letter.letter
                else:
                    current_player.letters += letter.letter
                letter.delete()

        tmp = list(game.letters)
        random.shuffle(tmp)
        game.letters = ''.join(tmp)
        
        if not current_player.left:
            _send_update(current_player.token, 'update_letters', {
                'letters': current_player.letters
            })

        current_player.save()
        game.save()

        _next_player(game, n_true >= n_false)
    return HttpResponse()
