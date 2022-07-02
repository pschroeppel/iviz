#!/usr/bin/env python3

from PyQt5.QtWidgets import QGridLayout, QWidget, QPushButton
from PyQt5.Qt import QSizePolicy, QSize, pyqtSignal
from PyQt5.QtGui import QIcon
from ...resources import display_highlight_border_width, viz_button_size, visible_icon_file, invisible_icon_file


class VisibilityButton(QWidget):
    toggled = pyqtSignal(bool)

    HORIZONTAL = "horizontal"
    VERTICAL = "vertical"

    def __init__(self, direction=HORIZONTAL, min_size=viz_button_size):
        super().__init__()
        self._direction = direction
        self._min_size = min_size
        self.initUI()

    def initUI(self):
        self._visible = True
        self._lay = QGridLayout()
        self._lay.setSpacing(0)
        self._button = QPushButton()
        self._button.clicked.connect(self._clicked)
        self._button.setIcon(QIcon(visible_icon_file.str()))
        self._button.setMinimumWidth(self._min_size)
        self._button.setMinimumHeight(self._min_size)
        self._button.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self._lay.addWidget(self._button)
        self.setLayout(self._lay)

        m = display_highlight_border_width
        self._lay.setContentsMargins(m, m, m, m)
        if self._direction == self.HORIZONTAL:  self._button.setMaximumHeight(self._min_size)
        else:                                   self._button.setMaximumWidth(self._min_size)

    def sizeHint(self):
        return QSize(viz_button_size + 2 * display_highlight_border_width, viz_button_size + 2 * display_highlight_border_width)

    def _clicked(self):
        self._update(not self._visible)

    def _update(self, value):
        if self._visible == value:
            return
        self._visible = value
        if not value: self._button.setIcon(QIcon(invisible_icon_file.str()))
        else: self._button.setIcon(QIcon(visible_icon_file.str()))
        self.toggled.emit(value)

    def setChecked(self, value):
        self._update(value)

    def button(self):
        return self._button

    def isChecked(self):
        return self._visible