#!/usr/bin/env python3

from ._pixviz import _PixmpVisualization
from PyQt5.QtCore import pyqtSignal


class ImagePixmapVisualization(_PixmpVisualization):
    viz_type_changed = pyqtSignal(str)

    def __init__(self, data=None):
        self._viz_type = 'RGB'
        super().__init__(data)

    def _update_image(self):
        if self._data is None or not self._data.image().valid():
            self._image = None
            self.changed.emit()
            return

        data = self._data.image().numpy()
        channels = data.shape[2]
        if channels == 1:
            pass
        elif channels == 3:
            if self._viz_type != "RGB":
                data = data[:, :, ::-1]
        elif channels == 2:
            raise Exception(f"ImageVisualization got {channels} channels but cannot handle grayscale alpha currently")
        elif channels == 4:
            raise Exception(f"ImageVisualization got {channels} channels but cannot handle RGB alpha currently")
        else:
            raise Exception(f"ImageVisualization got invalid number of channels: {channels}")

        self._image = data
        self.changed.emit()

    def is_grayscale(self):
        if self._data is None or not self._data.image().valid():
            return False
        data = self._data.image().numpy()
        channels = data.shape[2]
        return channels < 3

    def viz_type(self):
        return self._viz_type

    def set_viz_type(self, type):
        if self._viz_type ==  type:
            return

        if type not in ["RGB", "BGR"]:
            raise Exception(f"\"{type}\" invalid for set_viz_type(type=...) must be \"RGB\" or \"BGR\"")
        self._viz_type = type
        self._update_image()
        self.viz_type_changed.emit(self._viz_type)

    def file(self):
        if self._data is None:
            return None
        return self._data.image().file()

    def image(self):
        return self._image

    def numpy_data(self):
        if self._data is None:
            return None
        return self._data.image().numpy()

    def numpy_slice_data(self):
        return self.numpy_data()
