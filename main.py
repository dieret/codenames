#!/usr/bin/env python3

# std
import logging

# 3rd
from flask import Flask, render_template
from flask_socketio import SocketIO, send, emit

# ours
from codenames.users import Users, User
from codenames.messages import Messages, Message
from codenames.playground import Playground


app = Flask(__name__)
app.config['SECRET_KEY'] = 'vnkdjnfjknfl1232#'
socketio = SocketIO(app)


users = Users()
playground = Playground.generate_new()
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
    """ Gets triggered by the frontend if a user connected, i.e., the browser
    window was opened by someone (not necessarily a login yet). """
    app.logger.info("user connected: " + str(json))
    update_chat_messages()


@socketio.on("login")
def handle_user_login_event(json):
    """ Gets triggered by the frontend if a user logs in. We trigger 'user_login'
    on the frontend of the client who made the request to tell whether the
    login was successful or not and update our user database and write a chat
    message to everyone.
    """
    app.logger.info("User logged in: " + str(json))
    success = True
    if not json["user"]:
        success = False
    if "team" not in json or not json["team"]:
        success = False
    if "role" not in json or not json["role"]:
        success = False
    return_json = {
        "user": json["user"],
        "success": success
    }
    app.logger.debug("Returning json: " + str(return_json))
    emit('user_login', return_json, callback=messageReceived)
    if success:
        msg = f"User {json['user']} has joined team {json['team']} as " \
              f"{json['role']}."
        write_chat_message("system", msg)
        users.add_user(User(json["user"], team=json["team"], role=json["role"]))


@socketio.on('chat_message_received')
def handle_chat_message_received(json, methods=('GET', 'POST')):
    """ Gets triggered by the frontend if a user submits a chat message.
    We add it to the list of chat messages and trigger a rebuild of the chat
    history in all clients."""
    app.logger.info('Received chat message: ' + str(json))
    if json["user"].strip() and json["message"].strip():
        global messages
        messages.add_message(Message(json["user"], json["message"]))
        update_chat_messages()


def write_chat_message(user: str, message: str) -> None:
    """ Write a chat message to everyone. """
    global messages
    messages.add_message(Message(user, message))
    update_chat_messages()


def update_chat_messages():
    """ Triggers an update of the chat history box in all clients. """
    return_json = {"message": messages.to_html()}
    socketio.emit('update_chat_messages', return_json, callback=messageReceived)


@socketio.on("tile_clicked")
def handle_tile_clicked_event(json):
    """ Gets triggered by the frontend if someone clicks on one of the tiles of
    the playground. We check if the corresponding user triggers anything by
    clicking and if yes, ask all sessions to request a playground update. """
    app.logger.info("Tile clicked: " + str(json))
    user = users[json["user"]]
    if user.role == "guesser":
        tile = playground.tiles[json["index"]]
        tile.clicked_by = user.name
        msg = f"User {user.name} (team {user.team}) has clicked on " \
              f"field '{tile.content}'."
        write_chat_message("system", msg)
        ask_all_sessions_to_request_playground_update()
    else:
        msg = f"Tile clicking ignored, because user {user.nameastin} is not " \
              f"of role 'guesser', but of role '{user.role}'."
        app.logger.info(msg)


@socketio.on("request_update_playground")
def update_playground(json):
    """ Gets triggered by the frontend (not from the backend!) and sends back
    the html for the playground.
    The reason that this should only be triggered by the backend is that we
    need to know the user's role before serving them html (a 'guesser' gets
    different html than an 'explainer') and we only have the username if they
    make the request, not we.
    """
    user = users[json["user"]]
    role = user.role
    app.logger.info(f"Handing HTML for viewer role {role} to user {user.name}")
    emit(
        'update_playground',
        {"playground_html": playground.to_html(user_role=role)}
    )


def ask_all_sessions_to_request_playground_update():
    """ If `update_playground` has to be called by the backend, how do we force
    everyone to update the playground? We kindly ask them to submit an
    update themselves. """
    socketio.emit("ask_all_sessions_to_request_update_playground")


if __name__ == '__main__':
    app.logger.setLevel(logging.DEBUG)
    socketio.run(app, debug=True)
