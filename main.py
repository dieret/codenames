#!/usr/bin/env python3

from flask import Flask, render_template
from flask_socketio import SocketIO


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


@socketio.on('my event')
def handle_my_custom_event(json, methods=('GET', 'POST')):
    print('received my event: ' + str(json))
    print(json)
    return_json = json.copy()
    global messages
    messages.append(json["message"])
    return_json["message"] = messages_to_html(messages)
    print("m", return_json["message"])
    socketio.emit('my response', return_json, callback=messageReceived)


@socketio.on("navigation_event")
def handle_navigation_event(json):
    print(str(json))
    direction = json["direction"]
    update_coordinates()


@socketio.on("login")
def handle_user_login_event(json):
    print(str(json))
    return_json = {
        "user": json["user"],
        "success": True
    }
    print(return_json)
    socketio.emit('user_login', return_json, callback=messageReceived)


def update_coordinates():
    socketio.emit('coordinate_update', {"coordinates": "asdf"}, callback=messageReceived)


if __name__ == '__main__':
    # NOTE: Deactive debug mode because it calls everything twice
    # https://stackoverflow.com/questions/49524270/
    # rt = RepeatedTimer(300, db.save, "backup.pickle")
    socketio.run(app, debug=True)
