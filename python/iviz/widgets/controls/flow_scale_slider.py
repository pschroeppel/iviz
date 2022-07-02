#!/usr/bin/env python3

from PyQt5.QtWidgets import QWidget, QHBoxLayout, QSlider, QDoubleSpinBox
from PyQt5.QtCore import pyqtSignal, Qt


class FlowScaleSlider(QWidget):
    valueChanged = pyqtSignal(float)

    def __init__(self, max=512):
        super().__init__()
        self._max = max
        self._value = 0
        self.initUI()

    def initUI(self):
        lay = QHBoxLayout()

        lay.setContentsMargins(0, 0, 0, 0)

        self._slider = QSlider()
        self._slider.setOrientation(Qt.Horizontal)
        self._slider.setMinimum(0)
        self._slider.setMaximum(int(self._max * 10.0))
        lay.addWidget(self._slider)

        self._input = QDoubleSpinBox()
        self._input.setValue(self._value)
        self._input.setAlignment(Qt.AlignRight)
        self._input.setMinimum(0.01)
        self._input.setMaximum(10000)
        self._input.setMaximumWidth(70)
        lay.addWidget(self._input)

        self._slider.valueChanged.connect(self._change_slider_value)
        self._input.valueChanged.connect(self.set_value)

        self.setLayout(lay)

    def value(self):
        return self._value

    def _change_slider_value(self, value):
        self.set_value(value / 10.0 + 0.01)

    def set_value(self, value):
        if self._value == value: return

        self._value = value

        self._slider.blockSignals(True)
        self._slider.setValue(int((value - 0.01) * 10))
        self._slider.blockSignals(False)
        self._input.setValue(value)

        self.valueChanged.emit(self._value)



