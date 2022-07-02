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

import itypes
from ..._baseviz import _BaseVisualization
from itypes import File, is_torch, is_numpy, is_str, TraceLogger
from itypes import convert_device, convert_dims


class _PixmpVisualization(_BaseVisualization):
    def __init__(self, data=None):
        self.__log = TraceLogger()
        self._image = None
        self._file = None
        super().__init__(data)

    def _update_image(self):
        raise NotImplementedError

    def set_data(self, data):
        self.__log.debug(f"set data to {'None' if data is None else type(data)}")
        self._data = data
        self._update_data()
        self._update_image()

        self.changed.emit()

    def props(self):
        return self._data.props()

    def data(self):
        return self._data

    def reload(self):
        self.__log.debug(f"called")
        if self._data is None:
            return
        self._data.reload()
        self.set_data(self._data)

    def file(self):
        raise NotImplementedError

    def image(self):
        raise NotImplementedError

    def valid(self):
        return self.numpy_data() is not None

    def numpy_data(self):
        raise NotImplementedError

    def numpy_slice_data(self):
        raise NotImplementedError