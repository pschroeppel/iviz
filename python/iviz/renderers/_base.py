#!/usr/bin/env python3
from builtins import NotImplementedError


class _BaseRenderer:
    def __init__(self):
        self._fade = False

    def set_fade(self, value):
        if self._fade == value:
            return
        self._fade = value

    def set_viewport_size(self, width, height):
        raise NotImplementedError

    def valid(self):
        raise NotImplementedError

    def set_data(self, data):
        raise NotImplementedError

    def render(self, painter):
        raise NotImplementedError