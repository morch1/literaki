
function redraw_letters() {
    $('.myletter').remove();
    for (let i = 0; i < my_letters.length; i++) {
        const letter = my_letters[i];
        const points = letter_points.get(letter);
        $('#myletter-slot-' + i).html(`
            <div id='myletter-${i}' class='myletter letter' ondragstart='on_letter_dragstart(event)' data-letter_id='${i}' data-letter='${letter}'>
                ${letter}
                ${points > 0 ? `<div class='letter-points'>${points}</div>` : ''}
            </div>
        `)
    }
}

function make_letters_draggable(d) {
    for (let i = 0; i < my_letters.length; i++) {
        $('#myletter-' + i).attr('draggable', d);
    }
}

function on_letter_dragstart(ev) {
    ev.dataTransfer.setData("literaki/letter-" + render_id, ev.target.id);
    ev.dataTransfer.effectAllowed = "move";
}

var placed_letters = new Map();

function on_field_drop(ev) {
    // TODO: check if field is allowed
    // TODO: blanks
    ev.preventDefault();
    letter = document.getElementById(ev.dataTransfer.getData("literaki/letter-" + render_id));
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

function prepare_turn() {
    $('.plylist-small').html('');
    $('#player-' + current_player_id + '-current').html('⮞');
    $('#myletters-checkboxes').hide();
    $('#btn_exchange').val('wymień');
    exchanging = false;
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
            $("#vote_buttons .game-btn").attr('disabled', voted);
        } else {
            $("#buttons").show()
            $("#vote_buttons").hide()
        }
    }
}

ws.addEventListener('message', function(event) {
    var data = JSON.parse(event.data);
    if (data['msg_type'] == 'player_left') {
        $('#player-name-' + data['player_id']).addClass('player_name_left');
        $('#letters_left').text(data['letters_left']);
    } else if (data['msg_type'] == 'vote_start') {
        voting = true;
        data['letters'].forEach(letter_data => {
            let points = letter_points.get(letter_data[0]);
            $(`#field-${letter_data[2]}-${letter_data[1]}`).append(`
            <div class="letter letter-undecided">
                ${letter_data[0]}
                ${points > 0 ? `<div class='letter-points'>${points}</div>` : ''}
            </div>`);
        });
        if (me_id != current_player_id) {
            $("#buttons").hide()
            $("#vote_buttons").show()
        }
    } else if (data['msg_type'] == 'vote_end') {
        voting = false;
        voted = false;
        $("#btn_submit").val("✔️");
        $("#btn_vote_accept").val("✔️");
        $("#btn_vote_reject").val("❌");
        $("#vote_buttons .game-btn").attr('disabled', false);
        $('#letters_left').text(data['letters_left']);
        if (data['accept']) {
            $(".letter-undecided").removeClass("letter-undecided");
        } else {
            $(".letter-undecided").remove();
            if (current_player_id == my_id) {
                alert('twoj ruch został odrzucony!');
            }
        }
        current_player_id = data['next_player'];
        prepare_turn();
    }
});

ws_priv.addEventListener('message', function(event) {
    var data = JSON.parse(event.data);
    if (data['msg_type'] == 'update_letters') {
        my_letters = data['letters'];
        redraw_letters();
    } 
});

exchanging = false;

$(function() {
    redraw_letters();
    prepare_turn();

    $('#btn_submit').click(function(){
        if (exchanging) {
            var exchanged_letters = [];
            for (let i = 0; i < 7; i++) {
                if ($('#myletter-exchange-' + i).is(':checked')) {
                    exchanged_letters.push(i)
                }
            }
            $.post('/game/' + game_token + '/exchange_letters', {
                letters: JSON.stringify(exchanged_letters)
            });
        } else {
            $.post('/game/' + game_token + '/place_letters', {
                letters: JSON.stringify(Object.fromEntries(placed_letters))
            });
            make_letters_draggable(false);
            $(this).val("⌛");
            $("#buttons .game-btn").attr('disabled', true);
            for ([i, data] of placed_letters.entries()) {
                $('#myletter-' + i).remove();
            }
            placed_letters = new Map();
        }
    });

    function vote(accept, btn) {
        voted = true;
        btn.val("⌛");
        $.post('/game/' + game_token + '/vote', {vote: accept});
        $("#vote_buttons .game-btn").attr('disabled', true);
    }
    
    $('#btn_vote_accept').click(function() {
        vote(1, $(this));
    });

    $('#btn_vote_reject').click(function() {
        vote(0, $(this));
    });

    $('#btn_exchange').click(function() {
        redraw_letters();
        if (exchanging) {
            $('#myletters-checkboxes').hide();
            $('.myletter-checkbox').hide();
            $(this).val('wymień');
            make_letters_draggable(true);
        } else {
            $('.myletter-checkbox').prop('checked', false);
            $('#myletters-checkboxes').show();
            for (let i = 0; i < my_letters.length; i++) {
                $('#myletter-exchange-' + i).show();
            }
            $(this).val('anuluj');
            make_letters_draggable(false);
        }
        exchanging = !exchanging;
    });
});
