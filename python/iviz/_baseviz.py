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

from itypes import addr, TraceLogger
from PyQt5.QtCore import QObject, pyqtSignal


class _BaseVisualization(QObject):
    changed = pyqtSignal()

    def __init__(self, data=None):
        self.__log = TraceLogger()
        super().__init__()
        self._data = None
        self.init_data(data)

    def init_data(self, data):
        self.set_data(data)

    def set_data(self, data):
        self.__log.debug(f"set data = {data}")
        self._data = data
        self.changed.emit()

    def _update_data(self):
        pass

