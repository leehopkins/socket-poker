$(document).ready(function() {
    var socket = io('/session', {'sync disconnect on unload': true});
    var getMessageItem = function(user, msg) {
        return $('<li>').addClass('list-group-item')
            .append($('<h4>').addClass('list-group-item-heading').text(user))
            .append($('<p>').addClass('list-group-item-text').text(msg));
    };

    $('#chat-send').click(function() {
        socket.emit('chat-message', $('#chat-input').val());
        $('#chat-input').val('');
    });

    $('#chat-input').keyup(function(evt) {
        if(evt.which !== 13) {
            return;
        }

        socket.emit('chat-message', $('#chat-input').val());
        $('#chat-input').val('')
    });

    $('.point-button').click(function(evt) {
        socket.emit('vote', $(evt.target).text());
    });

    $('#set-topic').click(function() {
        socket.emit('set-topic', $('#topic').val());
    });

    $('#topic').keyup(function(evt) {
        if(evt.which !== 13) {
            return;
        }

        socket.emit('set-topic', $('#topic').val());
    });

    $('#show-votes').click(function() {
        socket.emit('show-votes');
    });

    $('#clear-votes').click(function() {
        socket.emit('clear-votes');
    });

    socket.on('joined', function(data) {
        if($('#' + data.id).length > 0) {
            return;
        }

        var $messages = $('#messages');
        $messages
            .append(getMessageItem(data.user, 'has joined the session'))
            .scrollTop($messages[0].scrollHeight);

        if(data.role == 'player') {
            $('#player-list').append($('<li>')
                .attr('id', data.id)
                .addClass('list-group-item')
                .text(data.user)
                .append('<span class="badge"><span class="player-vote glyphicon glyphicon-remove"></span></span>'));
        }
    });

    socket.on('chat-message', function(data) {
        var $messages = $('#messages');
        $messages
            .append(getMessageItem(data.user, data.message))
            .scrollTop($messages[0].scrollHeight);
    });

    socket.on('set-topic', function(topic) {
        $('#voting-on').text(topic);
    });

    socket.on('vote', function(data) {
        var $vote = $('#' + data.id + ' span.player-vote').data('points', data.points);
        if($vote.hasClass('glyphicon')) {
            $vote.removeClass('glyphicon-remove').addClass('glyphicon-ok');
        }
        else {
            $vote.text(data.points)
        }
    });

    socket.on('show-votes', function() {
        $('#player-list span.glyphicon-ok')
            .each(function(idx, ele){
                var $ele = $(ele);
                $ele.removeClass('glyphicon glyphicon-ok').text($ele.data('points'));
            });
    });

    socket.on('clear-votes', function(data) {
        $('#player-list span.player-vote')
            .empty()
            .removeData()
            .addClass('glyphicon glyphicon-remove');
    });

    socket.on('left', function(data) {
        $('#' + data.id).remove();
        var $messages = $('#messages');
        $messages
            .append(getMessageItem(data.user, 'has left the session'))
            .scrollTop($messages[0].scrollHeight);
    });
});
