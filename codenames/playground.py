#!/usr/bin/env python3

# std
from typing import List, Optional
import random

# ours
from codenames.users import User


class PlaygroundTile(object):
    def __init__(self, content: str, tile_type: str, index: int):
        #: HTML content to display?
        self.content = content

        #: Index in the playground
        self.index = index

        #: blue, red, bomb, none
        self.type = tile_type

        self.clicked_by = None  # type: Optional[User]


    @property
    def was_clicked(self) -> bool:
        return self.clicked_by is not None

    def point_for(self, team: str) -> int:
        if self.was_clicked and team == self.type:
            return 1
        else:
            return 0

    @property
    def correctly_clicked(self) -> Optional[bool]:
        """ Returns true if was clicked correctly, false otherwise. If not
        clicked at all, return None"""
        if not self.was_clicked:
            return None
        else:
            if self.clicked_by.team == self.type:
                return True
            else:
                return False

    def get_tile_class(self, user_role: str) -> str:
        classes = []

        if self.clicked_by is not None or user_role == "explainer":
            classes.append(self.type)

        if self.clicked_by is not None:
            classes.append("clicked")
        else:
            classes.append("unclicked")

        classes.append(user_role)

        return " ".join(classes)

    def to_html(self, user_role: str) -> str:
        attributes = [
            f'id="tile{self.index}"',
            f'class="tile {self.get_tile_class(user_role=user_role)}"',
        ]
        if self.clicked_by is None:
            attributes.append(f'onclick="tileClicked({self.index})"')
        return f'<a {" ".join(attributes)} >{self.content}</a>'


class Playground(object):
    def __init__(self, tiles: List[PlaygroundTile]):
        self.tiles = tiles
        #: Number of columns in which the tiles are presented
        self.ncols = 6

    def to_html(self, user_role) -> str:
        out = ""
        for i, field in enumerate(self.tiles):
            if i > 0 and i % self.ncols == 0:
                out += "<br/>"
            out += field.to_html(user_role=user_role)
        return out

    def get_score(self):
        points = {
            "red": 0,
            "blue": 0
        }
        for tile in self.tiles:
            for team in ["red", "blue"]:
                points[team] += tile.point_for(team)
        return points

    @classmethod
    def generate_new(cls):
        fields = []
        for i in range(36):
            fields.append(PlaygroundTile("word", random.choice(["red", "blue", "bomb"]), i))
        return cls(fields)
