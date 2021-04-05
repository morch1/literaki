
function redraw_letters() {
    for (let i = 0; i < my_letters.length; i++) {
        const letter = my_letters[i];
        $('#myletter-slot-' + i).html(`<div id='myletter-${i}' class='letter' ondragstart='on_letter_dragstart(event)'>${letter}</div>`)
    }
    for (let i = my_letters.length; i < 7; i++) {
        $('#myletter-slot-' + i).html('')
    }
}

function make_letters_draggable(d) {
    for (let i = 0; i < my_letters.length; i++) {
        $('#myletter-' + i).attr('draggable', d);
    }
}

function on_letter_dragstart(ev) {
    ev.dataTransfer.setData("literaki/letter", ev.target.id);
    ev.dataTransfer.effectAllowed = "move";
}

function on_field_drop(ev) {
    ev.preventDefault();
    const data = ev.dataTransfer.getData("literaki/letter");
    ev.target.appendChild(document.getElementById(data));
}

function on_field_dragover(ev) {
    if (ev.target.innerHTML != '') return;
    ev.preventDefault();
    ev.dataTransfer.dropEffect = "move"
}

ws.addEventListener('message', function(event) {
    var data = JSON.parse(event.data);
    if (data['msg_type'] == 'player_left') {
        $('#player-' + data['player_id']).remove()
        // TODO: update current player
    }
});

$(function() {
    redraw_letters();
    if (current_player_id == me_id) {
        make_letters_draggable(!voting);
        $("#buttons .game-btn").attr('disabled', voting);
        $("#buttons").show()
        $("#vote_buttons").hide()
    } else {
        make_letters_draggable(false);
        $("#buttons .game-btn").attr('disabled', true);
        if (voting) {
            $("#buttons").hide()
            $("#vote_buttons").show()    
        } else {
            $("#buttons").show()
            $("#vote_buttons").hide()
        }
    }
});
