#!/usr/bin/env python3

# std
from typing import Dict


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