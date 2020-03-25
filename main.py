#!/usr/bin/env python3

from flask import Flask, render_template
from flask_socketio import SocketIO
import logging
from typing import List, Optional, Dict
import random


app = Flask(__name__)
app.config['SECRET_KEY'] = 'vnkdjnfjknfl1232#'
socketio = SocketIO(app)


class User(object):
    def __init__(self, name: str, team: str, role: str):
        self.name = name
        #: Team: 'red' or 'blue'
        self.team = team
        #: Role: 'guesser' or 'explainer'
        self.role = role


class Users(object):
    def __init__(self):
        self._username2user = {}  # type: Dict[str, User]

    def add_user(self, user: User):
        self._username2user[user.name] = user

    def __getitem__(self, item: str):
        return self._username2user[item]


users = Users()


class PlaygroundTile(object):
    def __init__(self, content: str, type: str, index):
        #: HTML content to display?
        self.content = content

        self.index = index

        #: blue, red, bomb, none
        self.type = type

        self.clicked_by = None

    def get_tile_class(self, viewer):
        if viewer == "guesser":
            # todo: must be clicked-wrong/right
            if self.clicked_by is None:
                return "unclicked"
            else:
                return "clicked"
        elif viewer == "explainer":
            if self.clicked_by is None:
                cls = "unclicked"
            else:
                cls = "clicked"
            if self.type == "blue":
                cls += "_blue"
            elif self.type == "red":
                cls += "_red"
            elif self.type == "bomb":
                cls += "_bomb"
            elif self.type == "none":
                cls += "_none"
            else:
                raise ValueError(f"Invalid type {self.type}")
            return cls
        else:
            raise ValueError

    def to_html(self, viewer):
        return f'<a onclick="tileClicked({self.index})" id="tile{self.index}" class="tile {self.get_tile_class(viewer=viewer)}">{self.content}</a>'


class PlayGround(object):
    def __init__(self, tiles: List[PlaygroundTile]):
        self.fields = tiles
        self.ncols = 6

    def to_html(self, viewer="player"):
        out = ""
        for i, field in enumerate(self.fields):
            if i > 0 and i % self.ncols == 0:
                out += "<br/>"
            out += field.to_html(viewer=viewer)
        return out


def generate_new_playground() -> PlayGround:
    fields = []
    for i in range(36):
        fields.append(PlaygroundTile("word", random.choice(["red", "blue", "bomb", "none"]), i))
    return PlayGround(fields)


playground = generate_new_playground()


@app.route('/')
def sessions():
    return render_template(
        'session.html',
    )


def messageReceived(methods=('GET', 'POST')):
    print('message was received!!!')



class Message(object):
    def __init__(self, user: str, message: str):
        self.user = user
        self.message = message

    def to_html(self):
        return f"{self.user}: {self.message}"


class Messages(object):
    def __init__(self):
        self.messages = []  # type: List[Message]

    def add_message(self, message: Message):
        self.messages.append(message)

    def to_html(self):
        return "<br/>".join([m.to_html() for m in self.messages])


messages = Messages()




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
    field = playground.fields[json["index"]]
    field.clicked_by = user.name
    tile = playground.fields[json["index"]]
    write_chat_message("system", f"User {user.name} (team {user.team}) has clicked on field '{field.content}'.")
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

    # NOTE: Deactive debug mode because it calls everything twice
    # https://stackoverflow.com/questions/49524270/
    # rt = RepeatedTimer(300, db.save, "backup.pickle")
    socketio.run(app, debug=True)
