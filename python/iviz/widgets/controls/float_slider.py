#!/usr/bin/env python3

from PyQt5.QtWidgets import QWidget, QHBoxLayout, QSlider, QDoubleSpinBox
from PyQt5.QtCore import pyqtSignal, Qt


class FloatSlider(QWidget):
    valueChanged = pyqtSignal(float)

    def __init__(self, min=0, max=1, limit=True):
        super().__init__()
        self._min = min
        self._max = max
        self._limit = limit
        self._value = min
        self.initUI()

    def initUI(self):
        lay = QHBoxLayout()

        lay.setContentsMargins(0, 0, 0, 0)

        self._slider = QSlider()
        self._slider.setOrientation(Qt.Horizontal)
        self._slider.setMinimum(0)
        self._slider.setMaximum(16384)
        lay.addWidget(self._slider)

        self._input = QDoubleSpinBox()
        self._input.setValue(self._value)
        self._input.setAlignment(Qt.AlignRight)
        if self._limit:
            self._input.setMinimum(self._min)
            self._input.setMaximum(self._max)
        else:
            self._input.setMinimum(-99999)
            self._input.setMaximum(99999)
        lay.addWidget(self._input)

        self._slider.valueChanged.connect(self._change_slider_value)
        self._input.valueChanged.connect(self.set_value)

        self.setLayout(lay)

    def value(self):
        return self._value

    def set_range(self, min, max):
        self._min = min
        self._max = max
        if self._limit:
            self._input.setMinimum(self._min)
            self._input.setMaximum(self._max)
        else:
            self._input.setMinimum(-99999)
            self._input.setMaximum(99999)

    def _change_slider_value(self, value):
        self.set_value(value / 16384 * (self._max - self._min))

    def set_value(self, value):
        if self._value == value: return

        self._value = value

        slider_value = value / (self._max - self._min) * 16384
        if slider_value < 0: slider_value = 0
        if slider_value > 16384: slider_value = 16384
        self._slider.setValue(int(slider_value))
        self._input.setValue(value)

        self.valueChanged.emit(self._value)



