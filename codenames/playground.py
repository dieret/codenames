#!/usr/bin/env python3

# std
from typing import List, Optional
import random
from pathlib import Path

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

    def get_tile_classes(self, user_role: str) -> List[str]:
        classes = []

        if self.clicked_by is not None or user_role == "explainer":
            classes.append(self.type)

        if self.clicked_by is not None:
            classes.append("clicked")
        else:
            classes.append("unclicked")

        classes.append(user_role)

        return classes

    def to_html(self, user_role: str) -> str:
        class_str = " ".join(self.get_tile_classes(user_role=user_role) + ["tile"])
        attributes = [
            f'id="tile{self.index}"',
            f'class="{class_str}"',
        ]
        if self.clicked_by is None:
            attributes.append(f'onclick="tileClicked({self.index})"')
        attribute_str = " ".join(attributes)
        return f'<span {attribute_str}><a>{self.content}</a></span>'


class Playground(object):
    def __init__(self, tiles: List[PlaygroundTile]):
        self.tiles = tiles
        #: Number of columns in which the tiles are presented
        self.ncols = 5

        self._winner = None

    def to_html(self, user_role) -> str:
        if self._winner:
            user_role = "explainer"
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

    def _get_all_tiles_clicked(self):
        return len([tile for tile in self.tiles if tile.was_clicked]) == len(self.tiles)

    def _get_clicked_bombs(self):
        return [tile for tile in self.tiles if tile.type == "bomb" and tile.was_clicked]

    def get_winner(self) -> Optional[str]:
        if self._winner:
            return self._winner
        clicked_bomb = self._get_clicked_bombs()
        winner = None
        if clicked_bomb:
            bomb = clicked_bomb[-1]
            if bomb.clicked_by.team == "red":
                winner = "blue"
            else:
                winner = "red"
        elif self._get_all_tiles_clicked():
            score = self.get_score()
            if score["red"] > score["blue"]:
                winner = "red"
            else:
                winner = "blue"

        self._winner = winner
        return winner

    @classmethod
    def generate_new(cls):
        fields = []
        
        # choose random words
        path = Path(__file__).parent.resolve().parent / "data" / "words.txt"
        with path.open() as f:
            all_words = f.readlines()
        all_words = [word.strip() for word in all_words if word.strip()]
        words = random.sample(all_words, 25)

        # set up card ownership
        blue_count = random.choice([8, 9])
        red_count = 17 - blue_count
        types = ["bomb"] + \
                ["red"] * red_count + \
                ["blue"] * blue_count + \
                ["none"] * 7
        random.shuffle(types)
        for i in range(25):
            fields.append(PlaygroundTile(words[i], types[i], i))
        return cls(fields)
