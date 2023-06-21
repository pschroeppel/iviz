#!/usr/bin/env python3

### --------------------------------------------- ###
### Part of iViz                                  ###
### (C) 2022 Eddy ilg (me@eddy-ilg.net)           ###
### Creative Commons                              ###
### Attribution-NonCommercial-NoDerivatives       ###
### 4.0 International License.                    ###
### Commercial use an redistribution prohibited.  ###
### See https://github.com/eddy-ilg/iviz          ###
### --------------------------------------------- ###

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