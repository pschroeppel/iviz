#!/usr/bin/env python3

from ...utils import clamp
from .range_slider import RangeSlider
from PyQt5.QtWidgets import QGridLayout, QWidget, QLabel, QDoubleSpinBox
from PyQt5.QtCore import pyqtSignal, Qt, QEvent


class FloatRangeSlider(QWidget):
    selection_changed = pyqtSignal(float, float)
    lower_value_changed = pyqtSignal(float)
    upper_value_changed = pyqtSignal(float)

    def __init__(self, min=0, max=1, lower_value=0, upper_value=1, parent=None, limit=False, spin_box_class=QDoubleSpinBox):
        super().__init__(parent)
        self._limit = limit
        self._lower_value = -100000
        self._upper_value = 100000
        self._spin_box_class = spin_box_class

        self.initUI()
        
        self.set_range(min, max)
        self.set_selection(lower_value, upper_value)

    def initUI(self):
        self._layout = QGridLayout()
        
        self._layout.setSpacing(2)
        self._layout.setContentsMargins(0, 0, 0, 0)

        self._lower_spin = self._spin_box_class(self)
        self._lower_spin.setAlignment(Qt.AlignRight)
        self._lower_spin.valueChanged.connect(self.set_lower_value)
        self._lower_spin.setKeyboardTracking(False)
        self._lower_spin.setStyleSheet("margin-bottom: -1px; margin-top: -1px")
        self._lower_spin.setMinimumWidth(70)
        self._layout.addWidget(self._lower_spin, 0, 0)

        self._upper_spin = self._spin_box_class(self)
        self._upper_spin.setAlignment(Qt.AlignRight)
        self._upper_spin.valueChanged.connect(self.set_upper_value)
        self._upper_spin.setKeyboardTracking(False)
        self._upper_spin.setStyleSheet("margin-bottom: -1px; margin-top: -1px")
        self._upper_spin.setMinimumWidth(70)
        self._layout.addWidget(self._upper_spin, 0, 1)

        self._slider = RangeSlider(min=0, max=16384, lower_value=0, upper_value=16384)
        self._layout.addWidget(self._slider, 1, 0, 1, 2)
        self._slider.lower_value_changed.connect(self._change_slider_lower_value)
        self._slider.upper_value_changed.connect(self._change_slider_upper_value)

        self.setLayout(self._layout)

    def _range_divider(self):
        if self._max != self._min:
            return (self._max - self._min)
        return 1

    def _to_slider_value(self, x):
        return int((x - self._min) * 16384 / self._range_divider())

    def _from_slider_value(self, x):
        return x / 16384 * self._range_divider() + self._min

    def set_range(self, min, max):        
        self._min = min 
        self._max = max

        if self._limit:
            new_lower_value = clamp(self._lower_value, min, max)
            new_upper_value = clamp(self._upper_value, min, max)
        else:
            new_lower_value = self._lower_value
            new_upper_value = self._upper_value

        if self._limit:
            self._lower_spin.setMinimum(self._min)
            self._lower_spin.setMaximum(new_upper_value)
            self._upper_spin.setMinimum(new_lower_value)
            self._upper_spin.setMaximum(self._max)
        else:
            self._lower_spin.setMinimum(-99999)
            self._lower_spin.setMaximum(new_upper_value)
            self._upper_spin.setMinimum(new_lower_value)
            self._upper_spin.setMaximum( 99999)

        self.set_lower_value(new_lower_value)
        self.set_upper_value(new_upper_value)

    def set_selection(self, lower_value, upper_value):
        self.set_lower_value(lower_value)
        self.set_upper_value(upper_value)

    def lower_value(self):
        return self._lower_value
    
    def upper_value(self):
        return self._upper_value

    def value(self):
        return self._value
    
    def selection(self):
        return (self.lower_value(), self.upper_value())

    def set_lower_value(self, value):
        if self._lower_value == value: 
            return 
        
        self._lower_value = value

        self._lower_spin.setValue(value)
        self._upper_spin.setMinimum(value)
        self._slider.blockSignals(True)
        self._slider.set_selection(
            self._to_slider_value(self._lower_value),
            self._to_slider_value(self._upper_value),
        )
        self._slider.blockSignals(False)

        self.lower_value_changed.emit(self._lower_value)
        self.selection_changed.emit(self._lower_value, self._upper_value)

    def set_upper_value(self, value):
        if self._upper_value == value: 
            return 
        
        self._upper_value = value

        self._upper_spin.setValue(value)
        self._lower_spin.setMaximum(value)
        self._slider.blockSignals(True)
        self._slider.set_selection(
            self._to_slider_value(self._lower_value),
            self._to_slider_value(self._upper_value),
        )
        self._slider.blockSignals(False)

        self.upper_value_changed.emit(self._upper_value)
        self.selection_changed.emit(self._lower_value, self._upper_value)

    def _change_slider_lower_value(self, value):
        self.set_lower_value(self._from_slider_value(value))

    def _change_slider_upper_value(self, value):
        self.set_upper_value(self._from_slider_value(value))
