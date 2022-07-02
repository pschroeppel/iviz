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

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSizePolicy, QGridLayout
from PyQt5.QtGui import QPainter, QColor
from PyQt5.QtCore import pyqtSignal, Qt, QSize
from ._base import _BaseDisplay
from ...resources import display_highlight_border_width
from ...renderers import TextRenderer
from itypes.vizdata import TextVisualizationData
from ...resources import display_highlight_border_width, viz_button_size, head_bar_button_size


class TextDisplay(_BaseDisplay):
    def __init__(self, manager=None, text="", data=None, id=None, label=None, valign=None, halign=None, width=None, height=None, template=None):
        super().__init__(manager, id, label)
        if valign is None: valign = "center"
        if halign is None: halign = "center"
        if template is None: template = "{text}"

        if "{text}" not in template:
            raise Exception("text template must contain {text} as a placeholder")

        self._pos = None
        self._data = None

        self._text = text
        self._valign = valign
        self._halign = halign
        self._width = width
        self._height = height
        self._template = template

        self.initUI()
        self.set_data(data)

        self._set_shrink_mode()

    def _set_shrink_mode(self):
        if self._width is None and self._height is None:
            return super()._set_shrink_mode()

        min_width = self._shrinking_minimum_size.width()
        min_height = self._shrinking_minimum_size.height()
        if self._width is not None: min_width = self._width
        if self._height is not None: min_height = self._height

        self._mode = "shrink"
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.setMinimumWidth(min_width)
        self.setMinimumHeight(min_height)

        if self.parent():
            self.parent().updateGeometry()

    def set_highlighted(self, value):
        pass
    
    def initUI(self):
        super().initUI()

        self._label = QLabel()

        valign = Qt.AlignVCenter
        if self._valign == "top": valign = Qt.AlignTop
        elif self._valign == "bottom": valign = Qt.AlignBottom
        elif self._valign == "center": valign = Qt.AlignVCenter
        else: raise Exception(f"invalid value for valign: {self._valign}")

        halign = Qt.AlignHCenter
        if self._halign == "left": halign = Qt.AlignLeft
        elif self._halign == "right": halign = Qt.AlignRight
        elif self._halign == "center": halign = Qt.AlignHCenter
        else: raise Exception(f"invalid value for halign: {self._halign}")

        self._label.setAlignment(valign | halign)

        m = display_highlight_border_width + 2
        self._layout = QGridLayout()
        self._layout.setContentsMargins(m, m, m, m)
        self._layout.addWidget(self._label)
        self.setLayout(self._layout)

    def sizeHint(self):
        s = super().sizeHint()
        width = s.width()
        if self._width is not None: width = self._width
        height = s.height()
        if self._height is not None: height = self._height
        return QSize(width, height)

    def set_data(self, data):
        text = self._text
        if data is not None:
            text = data.text().data()

        templated = self._template.replace("{text}", text)
        self._label.setText(templated)

    def paintEvent(self, e):
        width = self.width()
        height = self.height()
        p = QPainter(self)
        s = display_highlight_border_width
        p.fillRect(0 + s, 0 + s, width - 2 * s, height - 2 * s, QColor('#dddddd'))

        super().paintEvent(e)



