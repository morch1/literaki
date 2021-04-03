
ws.addEventListener('message', function(event) {
    var data = JSON.parse(event.data);
    if (data['msg_type'] == 'player_joined') {
        $('#plylist').append(
            `<li id="player-${data["player_id"]}"><span id="player-name-${data["player_id"]}">${data["player_name"]}</span></li>`
        )
    } else if (data['msg_type'] == 'player_left') {
        $('#player-' + data['player_id']).remove()
    } else if (data['msg_type'] == 'player_ready') {
        $('#player-' + data['player_id']).append(' ✔️')
    } else if (data['msg_type'] == 'game_started') {
        setTimeout(() => {  location.reload(); }, 1000);
    }
});

$(function(){
    $('#change_name').click(function(){
        $.post('/game/' + game_token + '/change_name', {
            new_name: $('#plyname').val()
        })
    });

    $('#start').click(function(){
        $.post('/game/' + game_token + '/ready')
        $(this).val('⌛')
        $(this).prop('disabled', true)
    });
});
