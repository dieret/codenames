#!/usr/bin/env python3

# std
import logging

# 3rd
from flask import Flask, render_template
from flask_socketio import SocketIO

# ours
from codenames.users import Users, User
from codenames.messages import Messages, Message
from codenames.playground import generate_new_playground


app = Flask(__name__)
app.config['SECRET_KEY'] = 'vnkdjnfjknfl1232#'
socketio = SocketIO(app)


users = Users()
playground = generate_new_playground()
messages = Messages()


@app.route('/')
def sessions():
    return render_template(
        'session.html',
    )


def messageReceived(methods=('GET', 'POST')):
    print('message was received!!!')


@socketio.on("user_connect")
def handle_user_connect(json, ):
    app.logger.info("user connected: " + str(json))
    update_chat_messages()


@socketio.on("login")
def handle_user_login_event(json):
    app.logger.info("User logged in: " + str(json))
    success = True
    if not json["user"]:
        success = False
    if not "team" in json or not json["team"]:
        success = False
    if not "role" in json or not json["role"]:
        success = False
    return_json = {
        "user": json["user"],
        "success": success
    }
    app.logger.debug("Returning json: " + str(return_json))
    socketio.emit('user_login', return_json, callback=messageReceived)
    if success:
        write_chat_message("system", f"User {json['user']} has joined team {json['team']} as {json['role']}.")
        users.add_user(User(json["user"], team=json["team"], role=json["role"]))


@socketio.on('chat_message_received')
def handle_chat_message_received(json, methods=('GET', 'POST')):
    app.logger.info('Received chat message: ' + str(json))
    if json["user"].strip() and json["message"].strip():
        global messages
        messages.add_message(Message(json["user"], json["message"]))
        update_chat_messages()


def write_chat_message(user, message):
    global messages
    messages.add_message(Message(user, message))
    update_chat_messages()


def update_chat_messages():
    return_json = {}
    return_json["message"] = messages.to_html()
    socketio.emit('update_chat_messages', return_json, callback=messageReceived)


@socketio.on("tile_clicked")
def handle_tile_clicked_event(json):
    app.logger.info("Tile clicked: " + str(json))
    user = users[json["user"]]
    tile = playground.tiles[json["index"]]
    tile.clicked_by = user.name
    write_chat_message("system", f"User {user.name} (team {user.team}) has clicked on field '{tile.content}'.")
    ask_all_sessions_to_request_playground_update()


@socketio.on("request_update_playground")
def update_playground(json=None):
    """ Should not be called from backend!!!  Rather use ask_all_sessions_to_request_playground_update"""
    if json is None:
        json = {}
    if "user" in json:
        role = users[json["user"]].role
    else:
        role = None
    socketio.emit('update_playground', {"playground_html": playground.to_html(viewer=role)}, callback=messageReceived)


def ask_all_sessions_to_request_playground_update():
    socketio.emit("ask_all_sessions_to_request_update_playground")


if __name__ == '__main__':
    app.logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    app.logger.addHandler(handler)

    socketio.run(app, debug=True)
