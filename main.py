import os
import redis
import uuid
from flask import Flask, render_template, session, redirect, url_for
from flask_socketio import SocketIO, emit, join_room, leave_room
from forms import CreateSessionForm

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.debug = True
socketio = SocketIO(app)
r = redis.from_url(os.environ.get('REDIS_URL'))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/create', methods=['GET', 'POST'])
def create_or_join():
    form = CreateSessionForm()

    if not form.validate_on_submit():
        return render_template('create.html', form=form)

    session_key = 'session:' + form.session_id.data
    if len(form.session_id.data) == 0:
        session_key = session_key + str(r.incr('session:idx'))
        r.hset(session_key, 'people_key', 'people:' + str(r.incr('people:idx')))

    uid = str(uuid.uuid4())
    r.sadd(r.hget(session_key, 'people_key'), uid)
    r.hmset(uid, { 'username': form.username.data, 'role': form.role.data, 'vote': '' })
    session['user_id'] = uid
    session['poker_session_id'] = session_key[8:]
    return redirect(url_for('view_session', sid=session_key[8:]))


@app.route('/session/<sid>')
def view_session(sid):
    uid = session.get('user_id')
    poker_session = r.hgetall('session:' + sid)
    if uid is None or not poker_session:
        return redirect(url_for('create_or_join'))

    role = r.hget(uid, 'role')
    poker_session['people'] = {}
    for pid in r.smembers(poker_session['people_key']):
        poker_session['people'][pid] = r.hgetall(pid)

    return render_template('session.html', role=role, poker_session=poker_session)

@socketio.on('connect', namespace='/session')
def joined():
    uid, sid = session.get('user_id'), session.get('poker_session_id')
    join_room(sid)
    user = r.hgetall(uid)
    emit('joined', { 'user': user['username'], 'id': uid, 'role': user['role'] }, room=sid)

@socketio.on('chat-message', namespace='/session')
def chat_message(message):
    uid, sid = session.get('user_id'), session.get('poker_session_id')
    emit('chat-message', { 'message': message, 'user': r.hget(uid, 'username') }, room=sid)

@socketio.on('set-topic', namespace='/session')
def set_topic(topic):
    uid, sid = session.get('user_id'), session.get('poker_session_id')
    if r.hget(uid, 'role') != 'admin':
        return;

    r.hset('session:' + sid, 'topic', topic)
    emit('set-topic', topic, room=sid)

@socketio.on('vote', namespace='/session')
def vote(points):
    uid, sid = session.get('user_id'), session.get('poker_session_id')
    if r.hget(uid, 'role') != 'player':
        return;

    r.hset(uid, 'vote', points)
    emit('vote', { 'points': points, 'user': r.hget(uid, 'username'), 'id': uid }, room=sid)

@socketio.on('show-votes', namespace='/session')
def show_votes():
    uid, sid = session.get('user_id'), session.get('poker_session_id')
    if r.hget(uid, 'role') != 'admin':
        return;

    emit('show-votes', room=sid)

@socketio.on('clear-votes', namespace='/session')
def clear_votes():
    uid, sid = session.get('user_id'), session.get('poker_session_id')
    if r.hget(uid, 'role') != 'admin':
        return;

    people_ids = r.smembers(r.hget('session:' + sid, 'people_key'))
    for pid in people_ids:
        r.hset(pid, 'vote', '')

    emit('clear-votes', room=sid)

@socketio.on('disconnect', namespace='/session')
def left():
    uid, sid = session.get('user_id'), session.get('poker_session_id')
    user = r.hgetall(uid)
    poker_session = r.hgetall('session:' + sid)
    r.delete(uid)
    r.srem(poker_session['people_key'], uid)
    if r.scard(poker_session['people_key']) == 0:
        r.delete(poker_session['people_key'], 'session:' + sid)

    leave_room(sid)
    emit('left', { 'user': user['username'], 'id': uid, 'role': user['role'] }, room=sid)

if __name__ == '__main__':
    socketio.run(app)
