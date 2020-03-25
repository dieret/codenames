#!/usr/bin/env python3

from flask import Flask, render_template
from flask_socketio import SocketIO
import logging


app = Flask(__name__)
app.config['SECRET_KEY'] = 'vnkdjnfjknfl1232#'
socketio = SocketIO(app)


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


@socketio.on('chat_message_received')
def handle_my_custom_event(json, methods=('GET', 'POST')):
    app.logger.info('Received chat message: ' + str(json))
    global messages
    messages.append(json["message"])
    return_json = {}
    return_json["message"] = messages_to_html(messages)
    socketio.emit('update_chat_messages', return_json, callback=messageReceived)



@socketio.on("login")
def handle_user_login_event(json):
    app.logger.info("User logged in: ", json)
    return_json = {
        "user": json["user"],
        "success": True
    }
    app.logger.debug("Returning json: " + str(return_json))
    socketio.emit('user_login', return_json, callback=messageReceived)


def update_coordinates():
    socketio.emit('coordinate_update', {"coordinates": "asdf"}, callback=messageReceived)


if __name__ == '__main__':
    app.logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    app.logger.addHandler(handler)

    # NOTE: Deactive debug mode because it calls everything twice
    # https://stackoverflow.com/questions/49524270/
    # rt = RepeatedTimer(300, db.save, "backup.pickle")
    socketio.run(app, debug=True)
