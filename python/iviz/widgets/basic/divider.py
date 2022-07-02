#!/usr/bin/env python3

from PyQt5.QtGui import QCursor, QPainter, QColor, QPixmap, QKeyEvent, QPalette
from PyQt5.QtWidgets import QGridLayout, QWidget, QApplication
from PyQt5.QtWidgets import QMenuBar, QAction, QMenu, QSizePolicy


class Divider(QWidget):
    HORIZONTAL = "horizontal"
    VERTICAL = "vertical"

    def __init__(self, direction=HORIZONTAL, size=1, color=QPalette().color(QPalette.Midlight)):
        self._direction = direction
        self._color = color
        super().__init__()
        if direction == self.HORIZONTAL:
            self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            self.setMinimumHeight(size)
            self.setMaximumHeight(size)
        else:
            self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
            self.setMinimumWidth(size)
            self.setMinimumWidth(size)

    def paintEvent(self, e):
        width = self.width()
        height = self.height()
        p = QPainter(self)
        p.fillRect(0, 0, width, height, self._color)

