
from literakiapp.models import Player, randid


def player_middleware(get_response):
    def middleware(request):
        session_player_token = request.session.get('player_token', randid())
        request.player, _ = Player.objects.get_or_create(token=session_player_token)
        request.session['player_token'] = request.player.token
        response = get_response(request)
        return response
    return middleware
