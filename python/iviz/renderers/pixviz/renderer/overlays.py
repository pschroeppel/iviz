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

from collections import OrderedDict
from PyQt5.QtCore import Qt, QPoint, QPointF, QRect, QRectF
from PyQt5.QtGui import QPixmap, QPainter, QColor, QBrush, QPen, QTransform


class Overlay:
    def paint(self, painter): raise NotImplementedError
    def clear_selection(self): pass


class CrosshairOverlay(Overlay):
    def __init__(self):
        self._pos = None
        self._int_pos = None

    def set_position(self, image_point):
        self._pos = image_point
        self._int_pos = self.to_int_position(image_point)

    def position(self):
        return self._pos

    def int_position(self):
        return self._int_pos

    def to_int_position(self, image_point):
        if isinstance(image_point, QPoint):
            return image_point
        x = int(image_point.x())
        y = int(image_point.y())
        return QPoint(x, y)

    def paint(self, painter):
        if self._int_pos is None:
            return
        width = painter.window().width()
        height = painter.window().height()
        x = self._int_pos.x() + 0.5 # Draw in the center of the pixel
        y = self._int_pos.y() + 0.5
        painter.drawLine(QPointF(0, y), QPointF(width, y))
        painter.drawLine(QPointF(x, 0), QPointF(x, height))

    def clear_selection(self):
        self._pos = None
        self._int_pos = None


class SelectionOverlay(Overlay):
    def __init__(self):
        self._region = None
        self._int_region = None

    def set_region(self, image_region):
        self._region = image_region
        self._int_region = self.to_int_region(image_region)
        if self._int_region is None:
            return

    def int_region(self):
        return self._int_region

    def to_int_region(self, image_region):
        if image_region is None:
            return None
        if isinstance(image_region, QRect):
            return image_region
        image_region = image_region.normalized()
        x1 = int(image_region.topLeft().x() + 0.5)
        y1 = int(image_region.topLeft().y() + 0.5)
        x2 = int(image_region.bottomRight().x() + 0.5)
        y2 = int(image_region.bottomRight().y() + 0.5)
        if x1 == x2 or y1 == y2:
            return None
        region = QRect(x1, y1, x2 - x1, y2 - y1)
        return region

    def region(self):
        return self._region

    def paint(self, painter):
        if self._int_region is None:
            return
        painter.drawRect(QRectF(self._int_region))

    def clear_selection(self):
        self._region = None
        self._int_region = None


class Overlays:
    def __init__(self):
        self._overlays = OrderedDict()
        self.add_overlay("crosshair", CrosshairOverlay())
        self.add_overlay("selection", SelectionOverlay())

    def add_overlay(self, name, overlay):
        self._overlays[name] = overlay

    def __getattr__(self, item):
        return self._overlays[item]

    def clear_selection(self):
        for overlay in self._overlays.values():
            overlay.clear_selection()

    def paint(self, painter):
        painter.setCompositionMode(QPainter.RasterOp_SourceXorDestination)
        painter.setPen(QPen(Qt.white, 0))
        for overlay in self._overlays.values():
            overlay.paint(painter)