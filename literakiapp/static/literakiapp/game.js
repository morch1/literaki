
ws.addEventListener('message', function(event) {
    var data = JSON.parse(event.data);
    if (data['msg_type'] == 'player_left') {
        $('#player-' + data['player_id']).remove()
        // TODO: update current player
    }
});
