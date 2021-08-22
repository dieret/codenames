#!/usr/bin/env python3

# std
import urllib.parse
import html


def handle_raw_input(string: str) -> str:
    """Decode URL encodings; make sure no HTML things are sneaked in."""
    return html.escape(urllib.parse.unquote(string))
