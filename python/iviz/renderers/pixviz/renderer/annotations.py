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

from PyQt5.QtCore import Qt, QPoint, QPointF
from PyQt5.QtGui import QPixmap, QPainter, QColor, QBrush, QPen, QTransform


class Annotations:
    def __init__(self):
        self._props = None

    def set_props(self, props):
        self._props = props

    def paint(self, painter):
        if self._props is None:
            return

        for ann in self._props.ann:
            ann.paint(painter)

