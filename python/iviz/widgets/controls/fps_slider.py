#!/usr/bin/env python3
import math

from PyQt5.QtWidgets import QWidget, QHBoxLayout, QSlider, QDoubleSpinBox, QLabel
from PyQt5.QtCore import pyqtSignal, Qt
import math


class FPSSlider(QWidget):
    valueChanged = pyqtSignal(float)

    def __init__(self, value=5, min=0.1, max=60):
        super().__init__()
        self._min = min
        self._max = max
        self._value = min
        self.initUI()

        self._a = min
        self._b = math.log(max / self._a) / 10000

        self.set_value(value)

    def initUI(self):
        lay = QHBoxLayout()

        lay.setContentsMargins(0, 0, 0, 0)

        self._slider = QSlider()
        self._slider.setOrientation(Qt.Horizontal)
        self._slider.setMinimum(0)
        self._slider.setMaximum(10000)
        self._slider.setTickInterval(1000)
        self._slider.setTickPosition(QSlider.TicksBothSides)
        lay.addWidget(self._slider)

        self._input = QDoubleSpinBox()
        self._input.setValue(self._value)
        self._input.setAlignment(Qt.AlignRight)
        self._input.setMinimum(self._min)
        self._input.setMaximum(self._max)
        lay.addWidget(self._input)

        self._label = QLabel("fps")
        lay.addWidget(self._label)

        self._slider.valueChanged.connect(self._change_slider_value)
        self._input.valueChanged.connect(self.set_value)

        self.setLayout(lay)

    def value(self):
        return self._value

    def _change_slider_value(self, value):
        value = self._a * math.exp(self._b * value)

        if self._value == value: return
        self._value = value

        self._input.blockSignals(True)
        self._input.setValue(value)
        self._input.blockSignals(False)

        self.valueChanged.emit(self._value)

    def set_value(self, value):
        if self._value == value: return
        self._value = value

        slider_value = math.log(value / self._a) / self._b
        if slider_value < 0: slider_value = 0
        if slider_value > 10000: slider_value = 10000
        self._slider.blockSignals(True)
        self._slider.setValue(int(slider_value))
        self._slider.blockSignals(False)
        self._input.blockSignals(True)
        self._input.setValue(value)
        self._input.blockSignals(False)

        self.valueChanged.emit(self._value)



