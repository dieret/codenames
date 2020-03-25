#!/usr/bin/env python3

# std
from typing import List


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

