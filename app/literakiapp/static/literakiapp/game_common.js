var ws_url = 'ws://' + window.location.host + '/ws/' + game_token + '/';
var ws = new ReconnectingWebSocket(ws_url);

var ws_priv_url = 'ws://' + window.location.host + '/ws/priv/' + ws_priv_id + '/';
var ws_priv = new ReconnectingWebSocket(ws_priv_url);

ws.addEventListener('message', function(event) {
    var data = JSON.parse(event.data);
    if (data['msg_type'] == 'player_name_changed') {
        $('#player-name-' + data['player_id']).text(data['new_name'])
    } else if (data['msg_type'] == 'player_left') {
        if (data['player_id'] == me_id) {
            ws.close();
            window.location.replace("/");
        }
    }
});

function kick_player(player_id){
    if (confirm('na pewno wyrzucić gracza? id: ' + player_id)) {
        $.post('/game/' + game_token + '/kick_player', {
            player_id: player_id
        });
        $("#kick-player-" + player_id).attr('disabled', true);
    }
}

$(function(){
    $('#change_name').click(function(){
        $.post('/game/' + game_token + '/change_name', {
            new_name: $('#plyname').val()
        })
    });

    $('#leave').click(function(){
        if (confirm('na pewno chcesz wyjść?')) {
            $.post('/game/' + game_token + '/leave')
        }
    });
});
