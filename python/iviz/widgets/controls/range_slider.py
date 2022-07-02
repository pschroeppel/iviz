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

from ...utils import clamp
from PyQt5.QtWidgets import QSizePolicy, QStyleOptionSlider, QStyle, QWidget, QApplication, QSlider
from PyQt5.QtCore import QRect, QSize, Qt, pyqtSignal
from PyQt5.QtGui import QPaintEvent, QPainter, QPalette, QMouseEvent, QBrush


class RangeSlider(QWidget):
    lower_value_changed = pyqtSignal(float)
    upper_value_changed = pyqtSignal(float)
    selection_changed = pyqtSignal(float, float)
    
    def __init__(self, min=0, max=10000, lower_value=0, upper_value=10000, parent=None):
        super().__init__(parent)

        self._min = min
        self._max = max

        self._slider = QStyleOptionSlider()
        self._slider.minimum = min
        self._slider.maximum = max 

        self._lower_position = lower_value
        self._upper_position = upper_value

        self.setSizePolicy(
            QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed, QSizePolicy.Slider)
        )

    def initUI(self):
        pass

    def set_range(self, minimum: int, maximum: int):
        self._min = minimum
        self._max = maximum
        self._slider.minimum = minimum
        self._slider.maximum = maximum

    def set_selection(self, start: int, end: int):
        lower_changed = False
        upper_changed = False

        if self._lower_position != start: 
            self._lower_position = clamp(start, self._min, self._max)
            lower_changed = True

        if self._upper_position != end:
            self._upper_position = clamp(end, self._min, self._max)
            upper_changed = True

        if lower_changed: self.lower_value_changed.emit(self._lower_position)
        if upper_changed: self.upper_value_changed.emit(self._upper_position)
        if lower_changed or upper_changed: self.selection_changed.emit(self._lower_position, self._upper_position)

        self.update()

    def get_selection(self):
        return (self._lower_position, self._upper_position)

    def paintEvent(self, event: QPaintEvent):
        painter = QPainter(self)

        # Draw rule
        self._slider.initFrom(self)
        self._slider.rect = self.rect()
        self._slider.sliderPosition = 0
        self._slider.subControls = QStyle.SC_SliderGroove | QStyle.SC_SliderTickmarks

        #   Draw groove
        self.style().drawComplexControl(QStyle.CC_Slider, self._slider, painter)

        #  Draw interval
        color = self.palette().color(QPalette.Highlight)
        color.setAlpha(160)
        painter.setBrush(QBrush(color))
        painter.setPen(Qt.NoPen)

        self._slider.sliderPosition = int(self._lower_position)
        x_left_handle = (
            self.style()
            .subControlRect(QStyle.CC_Slider, self._slider, QStyle.SC_SliderHandle)
            .right()
        )

        self._slider.sliderPosition = int(self._upper_position)
        x_right_handle = (
            self.style()
            .subControlRect(QStyle.CC_Slider, self._slider, QStyle.SC_SliderHandle)
            .left()
        )

        groove_rect = self.style().subControlRect(
            QStyle.CC_Slider, self._slider, QStyle.SC_SliderGroove
        )

        selection = QRect(
            x_left_handle,
            groove_rect.y(),
            x_right_handle - x_left_handle,
            groove_rect.height(),
        ).adjusted(-1, 1, 1, -1)

        painter.drawRect(selection)

        # Draw first handle
        self._slider.subControls = QStyle.SC_SliderHandle
        self._slider.sliderPosition = int(self._lower_position)
        self.style().drawComplexControl(QStyle.CC_Slider, self._slider, painter)

        # Draw second handle
        self._slider.sliderPosition = int(self._upper_position)
        self.style().drawComplexControl(QStyle.CC_Slider, self._slider, painter)

    def mousePressEvent(self, event: QMouseEvent):
        self._slider.sliderPosition = self._lower_position
        self._first_sc = self.style().hitTestComplexControl(
            QStyle.CC_Slider, self._slider, event.pos(), self
        )

        self._slider.sliderPosition = self._upper_position
        self._second_sc = self.style().hitTestComplexControl(
            QStyle.CC_Slider, self._slider, event.pos(), self
        )

    def mouseMoveEvent(self, event: QMouseEvent):
        distance = self._slider.maximum - self._slider.minimum

        pos = self.style().sliderValueFromPosition(
            0, distance, event.pos().x(), self.rect().width()
        )

        if self._second_sc == QStyle.SC_SliderHandle:
            if pos >= self._lower_position:
                if self._upper_position != pos:
                    self._upper_position = pos
                    self.upper_value_changed.emit(self._upper_position)
                    self.selection_changed.emit(self._upper_position, self._upper_position)
                self.update()

        elif self._first_sc == QStyle.SC_SliderHandle:
            if pos <= self._upper_position:
                if self._lower_position != pos:
                    self._lower_position = pos
                    self.lower_value_changed.emit(self._lower_position)
                    self.selection_changed.emit(self._lower_position, self._upper_position)
                self.update()
                return


    def sizeHint(self):
        slider_length = 84

        w = slider_length
        h = self.style().pixelMetric(QStyle.PM_SliderThickness, self._slider, self)

        return (
            self.style()
            .sizeFromContents(QStyle.CT_Slider, self._slider, QSize(w, h), self)
            .expandedTo(QApplication.globalStrut())
        )