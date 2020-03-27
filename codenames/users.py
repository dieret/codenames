#!/usr/bin/env python3

# std
from typing import Dict, List


class User(object):
    def __init__(self, name: str, team: str, role: str):
        self.name = name
        #: Team: 'red' or 'blue'
        self.team = team
        #: Role: 'guesser' or 'explainer'
        self.role = role

    def to_html(self, style="user-team"):
        if style == "user-team":
            return f'<span class="badge {self.team}">{self.name.capitalize()}</span>'
        elif style == "user-role":
            inside = self.name.capitalize()
            if not self.role == "guesser":
                inside += f" ({self.role})"
            out = f'<span class="badge {self.team}">{inside}</span>'
            return out
        else:
            raise ValueError(style)


class Users(object):
    def __init__(self):
        self._username2user = {}  # type: Dict[str, User]

    def add_user(self, user: User):
        self._username2user[user.name] = user

    def get_by_team(self, team: str) -> List[User]:
        return [
            user for user in self._username2user.values()
            if user.team == team
        ]

    def __getitem__(self, item: str):
        return self._username2user[item]