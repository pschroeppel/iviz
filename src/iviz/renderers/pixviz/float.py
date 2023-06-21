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

import numpy as np
from itypes import Struct, addr, TraceLogger
from copy import copy
from ._pixviz import _PixmpVisualization
from iutils import heatmap_viz
from PyQt5.QtCore import pyqtSignal


class FloatPixmapVisualization(_PixmpVisualization):
    range_min_changed = pyqtSignal(float)
    range_max_changed = pyqtSignal(float)
    viz_type_changed = pyqtSignal(str)

    def __init__(self, data=None, range_min=0, range_max=1):
        self.__log = TraceLogger()
        self._viz_type = 'heatmap'
        self._range_min = range_min
        self._range_max = range_max
        super().__init__(data)

    def file(self):
        if self._data is None:
            return None
        return self._data.float().file()

    def image(self):
        return self._image

    def numpy_data(self):
        if self._data is None:
            return None
        return self._data.float().numpy()

    def num_axes(self):
        if self._data is None:
            return None
        return len(self._data.shape)

    def _update_data(self):
        if self._data is None or not self._data.float().valid():
            return

        data = self._data.float().numpy()

        self._range_min = data[np.logical_not(np.isnan(data))].min()
        self._range_max = data[np.logical_not(np.isnan(data))].max()

    def _update_image(self):
        if self._data is None or not self._data.float().valid():
            self._image = None
            self.changed.emit()
            return

        # Extract HWC data
        data = self.numpy_slice_data()
        self.__log.debug(f"data.shape={self._data.float().data().shape}")
        self.__log.debug(f"numpy_slice_data().shape={data.shape}")
        self.__log.debug(f"range_min={self._range_min}, range_max={self._range_max}")

        # Render the data
        if self._viz_type == 'grayscale':
            transformed = (data - float(self._range_min)) / (float(self._range_max) - float(self._range_min))
            transformed[transformed > 1] = 1
            transformed[transformed < 0] = 0
            self._image = (transformed[:, :, 0] * 255.0).astype(np.uint8)

        elif self._viz_type == 'rgb':
            transformed = (data - float(self._range_min)) / (float(self._range_max) - float(self._range_min))
            transformed[transformed > 1] = 1
            transformed[transformed < 0] = 0
            self._image = (transformed[:, :, :] * 255.0).astype(np.uint8)

        elif self._viz_type == 'heatmap':
            heatmap = heatmap_viz(data[:, :, 0], self._range_min, self._range_max)
            self._image = heatmap.astype(np.uint8)

        else:
            raise Exception('invalid viztype')

        self.changed.emit()

    def viz_type(self): return self._viz_type

    def range_min(self): 
        self.__log.debug(f'range_min = {self._range_min}')
        return self._range_min

    def range_max(self): 
        self.__log.debug(f'range_min = {self._range_max}')
        return self._range_max

    def numpy_slice_data(self):
        if self._data is None or not self._data.float().valid():
            return

        data = self._data.float().numpy()

        # Return HWC
        if len(data.shape) == 3:
            return data
        elif len(data.shape) == 2:
            return np.expand_dims(data, 2)
        else:
            return np.expand_dims(np.expand_dims(data, 0), 2)

    def set_viz_type(self, type):
        if self._viz_type ==  type:
            return

        if type not in ["heatmap", "grayscale", "rgb"]:
            raise Exception(f"\"{type}\" invalid for set_viz_type(type=...) must be \"heatmap\", \"grayscale\" or \"rgb\"")
        self._viz_type = type
        self._update_image()
        self.viz_type_changed.emit(self._viz_type)

    def data_index(self, x, y):
        return (y, x, 0)

    def min_value(self):
        data = self.numpy_data()
        return data[np.logical_not(np.isnan(data))].min()

    def max_value(self):
        data = self.numpy_data()
        return data[np.logical_not(np.isnan(data))].max()

    def set_range_min(self, value):
        self.__log.trace(f"value = {value}")
        if self._range_min == value:
            return

        self._range_min = value
        self._update_image()
        self.range_min_changed.emit(self._range_min)

    def set_range_max(self, value):
        self.__log.trace(f"value = {value}")
        if self._range_max == value:
            return

        self._range_max = value
        self._update_image()
        self.range_max_changed.emit(self._range_max)

    def range_to_channel(self):
        data = self.numpy_slice_data()
        min = data[np.logical_not(np.isnan(data))].min()
        max = data[np.logical_not(np.isnan(data))].max()
        self.set_range_min(min)
        self.set_range_max(max)

    def range_to_all(self):
        data = np.nan_to_num(self.numpy_slice_data())
        min = data[np.logical_not(np.isnan(data))].min()
        max = data[np.logical_not(np.isnan(data))].max()
        self.set_range_min(min)
        self.set_range_max(max)
