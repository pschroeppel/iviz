#!/usr/bin/env python

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

