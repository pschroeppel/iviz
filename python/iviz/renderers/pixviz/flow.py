#!/usr/bin/env python3

from ._pixviz import _PixmpVisualization
from iutils import flow_viz
from PyQt5.QtCore import pyqtSignal


class FlowPixmapVisualization(_PixmpVisualization):
    viz_type_changed = pyqtSignal(str)
    scale_changed = pyqtSignal(float)

    def __init__(self, data=None, scale=1.0):
        self._viz_type = 'middlebury'
        self._scale = scale
        super().__init__(data)

    def file(self):
        if self._data is None:
            return None
        return self._data.flow().file()

    def image(self):
        return self._image

    def numpy_data(self):
        if self._data is None:
            return None
        return self._data.flow().numpy()

    def numpy_slice_data(self):
        return self.numpy_data()

    def range_to_max(self):
        np_data = self.numpy_data()
        if np_data is None: return

        import numpy as np
        mag = np.sqrt(np.sum(np.square(np_data), axis=2))
        max_val = mag.max()

        self.set_scale(max_val)

    def range_to_auto(self):
        np_data = self.numpy_data()
        if np_data is None: return

        import numpy as np
        mag = np.sqrt(np.sum(np.square(np_data), axis=2))

        hist, bin_edges = np.histogram(mag, bins=200, normed=True)

        threshold = 0.10
        i = len(hist) - 1
        value = 0
        while value < threshold:
            print(hist[i])
            value += hist[i]
            edge = bin_edges[i]
            i -= 1

        self.set_scale(edge)

    def _update_image(self):
        if self._data is None or not self._data.flow().valid():
            self._image = None
            self.changed.emit()
            return

        data = self._data.flow().numpy()
        if data.shape[2] != 2:
            raise Exception(f"FlowVisualization data must have 2 channels (got {data.shape[2]} instead)")

        self._image = flow_viz(data, self._scale, self._viz_type)

        self.changed.emit()

    def viz_type(self):
        return self._viz_type

    def scale(self):
        return self._scale

    def set_viz_type(self, type):
        if self._viz_type ==  type:
            return

        if type not in ["sintel", "middlebury"]:
            raise Exception(f"\"{type}\" invalid for set_viz_type(type=...) must be \"sintel\" or \"middlebury\"")
        self._viz_type = type
        self._update_image()
        self.viz_type_changed.emit(self._viz_type)

    def set_scale(self, scale):
        if self._scale == scale:
            return

        self._scale = scale
        self._update_image()
        self.scale_changed.emit(self._scale)

