#!/usr/bin/env python3

from PyQt5.QtWidgets import QGridLayout, QWidget, QPushButton, QLayout, QWidgetItem
from PyQt5.Qt import QSizePolicy, QSize, pyqtSignal, Qt
from PyQt5.QtGui import QIcon, QPalette, QColor, QDrag, QPixmap
from ....resources import display_highlight_border_width, viz_button_size, display_color


class DisplayPlaceholder(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        m = display_highlight_border_width
        self._lay = QGridLayout()
        self._lay.setSpacing(0)
        self._lay.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self._lay)

        self._widget = QWidget()
        p = QPalette()
        p.setColor(self.backgroundRole(), display_color)
        self._widget.setPalette(p)
        self._widget.setAutoFillBackground(True)
        self._lay.addWidget(self._widget)

        self.setMinimumWidth(viz_button_size)
        self.setMinimumHeight(viz_button_size)

    def set_hide_completely(self, value): pass
    def set_index(self, pos): pass