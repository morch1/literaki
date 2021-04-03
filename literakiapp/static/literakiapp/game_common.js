var ws_url = 'ws://' + window.location.host + '/ws/' + game_token + '/';
var ws = new ReconnectingWebSocket(ws_url);

ws.addEventListener('message', function(event) {
    console.log(event);
    var data = JSON.parse(event.data);
    if (data['msg_type'] == 'player_name_changed') {
        $('#player-name-' + data['player_id']).text(data['new_name'])
    }
});

$(function(){
    $('#leave').click(function(){
        if (confirm('na pewno chcesz wyjść?')) {
            ws.close();
            window.location.replace('/game/' + game_token + '/leave');
        }
    });
});
