#!/usr/bin/env python3

from PyQt5.QtWidgets import QWidget, QHBoxLayout, QSlider, QSpinBox
from PyQt5.QtCore import pyqtSignal, Qt


class IntSlider(QWidget):
    value_changed = pyqtSignal(int)

    def __init__(self, range):
        super().__init__()
        self._range = range
        self._value = range[0]
        self._changing = False
        self.initUI()

    def initUI(self):
        lay = QHBoxLayout()

        lay.setContentsMargins(0, 0, 0, 0)

        self._slider = QSlider()
        self._slider.setOrientation(Qt.Horizontal)
        self._slider.setMinimum(self._range[0])
        self._slider.setMaximum(self._range[1])
        lay.addWidget(self._slider)

        self._input = QSpinBox()
        self._input.setValue(self._value)
        self._input.setAlignment(Qt.AlignRight)
        self._input.setMinimum(self._range[0])
        self._input.setMaximum(self._range[1])
        lay.addWidget(self._input)

        self._slider.valueChanged.connect(self._change_slider_value)
        self._input.valueChanged.connect(self.change_value)

        self.setLayout(lay)

    def set_range(self, range):
        value = self.value()

        self._range = range
        self._slider.setMinimum(self._range[0])
        self._slider.setMaximum(self._range[1])
        self._input.setMinimum(self._range[0])
        self._input.setMaximum(self._range[1])

        if value < self._range[0]: self.change_value(self._range[0])
        if value > self._range[1]: self.change_value(self._range[1])

    def value(self):
        return self._value

    def _change_slider_value(self, value):
        self.change_value(value)

    def change_value(self, value):
        if self._value == value or self._changing: return

        self._changing = True
        self._value = value
        self._slider.setValue(value)
        self._input.setValue(value)
        self.value_changed.emit(self._value)
        self._changing = False


