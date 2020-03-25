#!/usr/bin/env python3

from flask import Flask, render_template
from flask_socketio import SocketIO
import logging
from typing import List


app = Flask(__name__)
app.config['SECRET_KEY'] = 'vnkdjnfjknfl1232#'
socketio = SocketIO(app)


class PlaygroundTile(object):
    def __init__(self, content: str, type: str, index):
        #: HTML content to display?
        self.content = content

        self.index = index

        #: blue, red, bomb, none
        self.type = type

        self.clicked_by = None

    def get_tile_class(self, viewer):
        if viewer == "player":
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
                raise ValueError(cls)
            return cls

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
        fields.append(PlaygroundTile("word", "?", i))
    return PlayGround(fields)


playground = generate_new_playground()


@app.route('/')
def sessions():
    return render_template(
        'session.html',
    )


def messageReceived(methods=('GET', 'POST')):
    print('message was received!!!')


messages = []


def messages_to_html(messages):
    return "<br/>".join(messages)


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


@socketio.on('chat_message_received')
def handle_chat_message_received(json, methods=('GET', 'POST')):
    app.logger.info('Received chat message: ' + str(json))
    global messages
    messages.append(json["message"])
    update_chat_messages()


def write_chat_message(message):
    global messages
    messages.append(message)
    update_chat_messages()


def update_chat_messages():
    return_json = {}
    return_json["message"] = messages_to_html(messages)
    socketio.emit('update_chat_messages', return_json, callback=messageReceived)


@socketio.on("tile_clicked")
def handle_tile_clicked_event(json):
    app.logger.info("Tile clicked: " + str(json))
    playground.fields[json["index"]].clicked_by = json["user"]
    write_chat_message(f"User {json['user']} has clicked on field with index {json['index']}")
    update_playground()


@socketio.on("request_update_playground")
def update_playground(json=None):
    if json is None:
        json = {}
    socketio.emit('update_playground', {"playground_html": playground.to_html()}, callback=messageReceived)


if __name__ == '__main__':
    app.logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    app.logger.addHandler(handler)

    # NOTE: Deactive debug mode because it calls everything twice
    # https://stackoverflow.com/questions/49524270/
    # rt = RepeatedTimer(300, db.save, "backup.pickle")
    socketio.run(app, debug=True)
