
ws.addEventListener('message', function(event) {
    var data = JSON.parse(event.data);
    if (data['msg_type'] == 'player_joined') {
        $('#plylist').append(`
            <tr id="player-${data["player_id"]}">
                <td id="player-${data["player_id"]}-ready"></td>
                <td id="player-name-${data["player_id"]}">${data["player_name"]}</td>
            </tr>`)
    } else if (data['msg_type'] == 'player_left') {
        $('#player-' + data['player_id']).remove()
    } else if (data['msg_type'] == 'player_ready') {
        $('#player-' + data['player_id'] + '-ready').append(' ✔️')
    } else if (data['msg_type'] == 'game_started') {
        setTimeout(() => {  location.reload(); }, 1000);
    }
});

$(function(){
    $('#start').click(function(){
        $.post('/game/' + game_token + '/ready')
        $(this).val('⌛')
        $(this).prop('disabled', true)
    });
});
