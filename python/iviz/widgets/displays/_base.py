#!/usr/bin/env python3

import math
from itypes import addr, TraceLogger
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSizePolicy, QMenu, QPushButton, QCheckBox, QGridLayout, QFrame, QLayout, QScrollArea
from PyQt5.QtGui import QPalette, QColor, QPainter, QPen
from PyQt5.QtCore import pyqtSignal, Qt, QMargins, QRect, QPoint, QSize
from ...resources import display_highlight_border_width, viz_button_size, display_color, expanding_minimum_size


class _BaseDisplay(QWidget):
    def __init__(self, manager=None, id=None, label=None):
        self.__log = TraceLogger()
        super().__init__()
        self._manager = manager
        self._manager.register_display(self)
        self._id = id
        self._label = label
        self._index = None
        self._faded = False

        self._expanding_minimum_size = expanding_minimum_size
        s = viz_button_size + 2 * display_highlight_border_width
        self._shrinking_minimum_size = QSize(s, s)
        self._set_expand_mode()

    def initUI(self):
        pass

    def _set_expand_mode(self):
        self._mode = "expand"
        self.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        size = self._expanding_minimum_size
        self.setMinimumWidth(size.width())
        self.setMinimumHeight(size.height())

        if self.parent():
            self.parent().updateGeometry()

    def _set_shrink_mode(self, size=None):
        self._mode = "shrink"
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        if size is None:
            size = self._shrinking_minimum_size
        width_hint = min(self.minimumSizeHint().width(), expanding_minimum_size.width())
        width = max(size.width(), width_hint)
        height_hint = min(self.minimumSizeHint().height(), expanding_minimum_size.height())
        height = max(size.height(), height_hint)
        self.setMinimumWidth(width)
        self.setMinimumHeight(height)

        if self.parent():
            self.parent().updateGeometry()

    def id(self): return self._id
    def index(self): return self._index

    def preferred_size(self):
        return QSize(10, 10)

    def set_highlighted(self, value):
        if self.parent() is not None:
            self.parent().set_highlighted(value)

    def reload(self):
        pass

    def set_show_controls(self, value):
        pass

    def set_index(self, index):
        self._index = index
        return self

    def update_property(self, property, value):
        pass

    def _update_contents_enabled(self):
        pass

    def set_faded(self, value):
        if self._faded == value:
            return

        self._faded = value

        self.__log.debug(f'value = {value}')
        self._update_contents_enabled()

    def enter(self):
        pass

    def leave(self):
        pass


