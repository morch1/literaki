
function redraw_letters() {
    for (let i = 0; i < my_letters.length; i++) {
        const letter = my_letters[i];
        $('#myletter-slot-' + i).html(`<div id='myletter-${i}' class='letter' ondragstart='on_letter_dragstart(event)' data-letter_id='${i}' data-letter='${letter}'>${letter}</div>`)
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

var placed_letters = new Map();

function on_field_drop(ev) {
    // TODO: check if field is allowed
    // TODO: blanks
    ev.preventDefault();
    letter = document.getElementById(ev.dataTransfer.getData("literaki/letter"));
    field = ev.target;
    field.appendChild(letter);
    if (field.dataset.x == -1) {
        placed_letters.delete(letter.dataset.letter_id)
    } else {
        placed_letters.set(letter.dataset.letter_id, [field.dataset.x, field.dataset.y]);
    }
}

function on_field_dragover(ev) {
    if (!ev.target.classList.contains('droppable') || ev.target.children.length > 0) return;
    ev.preventDefault();
    ev.dataTransfer.dropEffect = "move"
}

ws.addEventListener('message', function(event) {
    var data = JSON.parse(event.data);
    if (data['msg_type'] == 'player_left') {
        $('#player-name-' + data['player_id']).addClass('player_name_left');
        $('#letters_left').text(data['letters_left']);
        // TODO: update current player
    } else if (data['msg_type'] == 'vote_start') {
        data['letters'].forEach(letter_data => {
            $(`#field-${letter_data[2]}-${letter_data[1]}`).append(`<div class="letter letter-undecided">${letter_data[0]}</div>`);
        });
        if (me_id != current_player_id) {
            $("#buttons").hide()
            $("#vote_buttons").show()
        }
    }
});

ws_priv.addEventListener('message', function(event) {
    var data = JSON.parse(event.data);
    if (data['msg_type'] == 'update_letters') {
        my_letters = data['letters'];
        redraw_letters();
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

    $('#btn_submit').click(function(){
        $.post('/game/' + game_token + '/place_letters', {
            letters: JSON.stringify(Object.fromEntries(placed_letters))
        });
        make_letters_draggable(false);
        $("#btn_submit").val("⌛");
        $("#buttons .game-btn").attr('disabled', true);
        for ([i, data] of placed_letters.entries()) {
            $('#myletter-' + i).remove();
        }
        placed_letters = new Map();
    });
});
