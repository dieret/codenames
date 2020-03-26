#!/usr/bin/env python3

# std
from typing import List
import random


class PlaygroundTile(object):
    def __init__(self, content: str, type: str, index):
        #: HTML content to display?
        self.content = content

        self.index = index

        #: blue, red, bomb, none
        self.type = type

        self.clicked_by = None

    def get_tile_class(self, viewer):
        classes = []

        if self.clicked_by is not None or viewer == "explainer":
            classes.append(self.type)

        if self.clicked_by is not None:
            classes.append("clicked")
        else:
            classes.append("unclicked")

        classes.append(viewer)

        return " ".join(classes)

    def to_html(self, viewer):
        attributes = [
            f'id="tile{self.index}"',
            f'class="tile {self.get_tile_class(viewer=viewer)}"',
        ]
        if self.clicked_by is None:
            attributes.append(f'onclick="tileClicked({self.index})"')
        return f'<a {" ".join(attributes)} >{self.content}</a>'


class PlayGround(object):
    def __init__(self, tiles: List[PlaygroundTile]):
        self.tiles = tiles
        self.ncols = 6

    def to_html(self, viewer="player"):
        out = ""
        for i, field in enumerate(self.tiles):
            if i > 0 and i % self.ncols == 0:
                out += "<br/>"
            out += field.to_html(viewer=viewer)
        return out


def generate_new_playground() -> PlayGround:
    fields = []
    for i in range(36):
        fields.append(PlaygroundTile("word", random.choice(["red", "blue", "bomb"]), i))
    return PlayGround(fields)
