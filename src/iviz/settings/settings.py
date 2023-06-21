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

from itypes import File, TraceLogger
from ..resources import settings_file
from collections import OrderedDict


class Settings:
    def __init__(self, file):
        super().__init__()
        self.__log = TraceLogger()
        self._file = File(file)
        self._values = OrderedDict()
        if self._file.exists():
            self.__log.debug(f"found settings")
            self._read()

    def read(self):
        self.__log.debug(f"reading settings from {self._file}")
        self._values = self._file.read()

    def write(self, file):
        self.__log.debug(f"writing settings to {self._file}")
        self._file.write(self._values)

    def __getitem__(self, item):
        if item in self._values:
            return self._values.item
        return None

    def __setitem__(self, key, value):
        self._values[key] = value
        self.write()


settings = Settings(settings_file)
