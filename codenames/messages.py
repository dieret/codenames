#!/usr/bin/env python3

# std
from typing import List, Optional

# ours
from codenames.users import User


class Message(object):
    def __init__(self, message: str, user: Optional[User] = None):
        self.user = user  # type: Optional[User]
        self.message = message

    def to_html(self):
        if self.user:
            return self.user.to_html() + " " + self.message
        else:
            return self.message


class Messages(object):
    def __init__(self):
        self.messages = []  # type: List[Message]

    def add_message(self, message: Message):
        self.messages.append(message)

    def to_html(self):
        return "<br/>".join([m.to_html() for m in self.messages])

