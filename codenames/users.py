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
            return f"{self.name} ({self.team})"
        elif style == "user-role":
            out = f"{self.name}"
            if not self.role == "guesser":
                out += f" ({self.role})"
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

    def get_team_overview_html(self) -> str:
        out = ""
        for team in ["red", "blue"]:
            out += f"<b>Team {team.capitalize()}</b>"
            for member in self.get_by_team(team):
                out += f'<div> {member.to_html("user-role")}</div>'
        return out

    def __getitem__(self, item: str):
        return self._username2user[item]