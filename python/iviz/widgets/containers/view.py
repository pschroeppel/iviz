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

from itypes import TraceLogger
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter
from PyQt5.QtCore import Qt, QSize, QPoint, QPointF, QRectF
from PyQt5.QtCore import pyqtSignal

from ...renderers.pixviz import PixelVisualizationRenderer


class View(QWidget):
    relative_zoom_set = pyqtSignal(float, QPointF)
    screen_zoom_set = pyqtSignal(float, QPointF)
    zoom_changed = pyqtSignal()
    pan_offset_set = pyqtSignal(QPoint)
    selected_pixel_changed = pyqtSignal(QPointF)
    selected_region_changed = pyqtSignal(QRectF)
    selection_cleared = pyqtSignal()
    deregister_pixviz = pyqtSignal()
    register_pixviz = pyqtSignal()
    interpolation_changed = pyqtSignal(bool)
    mouse_hovered = pyqtSignal(QPointF)

    def __init__(self, manager=None):
        self.__log = TraceLogger()
        super().__init__()
        self._manager = manager
        self._renderer = PixelVisualizationRenderer()
        self._last_mouse_pos = None
        self._mouse_moved = False
        self._shared_mode = True
        self._has_selection = False
        self.setMouseTracking(True)
        self._end_action()

    def last_mouse_pos(self): return self._last_mouse_pos

    def renderer(self):
        return self._renderer

    def minimumSizeHint(self):
        return QSize(50, 50)

    def preview(self, widget_point, zoom=1.0, width=100, height=100):
        return self._renderer.render_preview(widget_point, zoom, width, height)

    def pixviz(self): return self._renderer._pixviz
    def set_pixviz(self, pixviz):
        if self._renderer._pixviz is not None:
            self.deregister_pixviz.emit()
            self._renderer._pixviz.changed.disconnect(self.update)
        self._renderer._pixviz = pixviz
        self._renderer._pixviz.changed.connect(self.update)
        self.register_pixviz.emit()

    def setEnabled(self, value):
        super().setEnabled(value)
        self._renderer.set_fade(not value)

    def interpolation(self): return self._renderer.interpolation()
    def set_interpolation(self, value):
        if self._renderer.set_interpolation(value):
            self.interpolation_changed.emit(value)
            self.update()

    def _is_outside_image(self, e):
        norm_coords = self._renderer.viewport_to_norm(e.pos())
        if norm_coords is None: return True
        if norm_coords.x() < 0 or norm_coords.x() > 1.0: return True
        if norm_coords.y() < 0 or norm_coords.y() > 1.0: return True
        return False

    def _end_action(self):
        self._mouse_down_pos = None
        self._left_down = False
        self._middle_down = False
        self._manager.update_preview_pos(QPoint())
        self.setCursor(Qt.CrossCursor)
        self.mouse_hovered.emit(QPointF())

    def _emit_signal(self, incoming_name, outgoing_name, *args, **kwargs):
        getattr(self, outgoing_name).emit(*args, **kwargs)
        if self._manager is not None and getattr(self._manager, incoming_name):
            getattr(self._manager, incoming_name)(*args, **kwargs)

    def select_pixel(self, norm_pos):
        overlay = self._renderer.overlays().crosshair
        image_pos = self._renderer.norm_to_image(norm_pos)
        if overlay.position() == image_pos:
            return
        self._renderer.overlays().clear_selection()
        self._renderer.overlays().crosshair.set_position(
            self._renderer.norm_to_image(norm_pos)
        )
        self._has_selection = True
        self._emit_signal("select_pixel", "selected_pixel_changed", norm_pos)
        self.update()

    def select_region(self, norm_region):
        overlay = self._renderer.overlays().selection
        tl = self._renderer.norm_to_image(norm_region.topLeft())
        br = self._renderer.norm_to_image(norm_region.bottomRight())
        if tl is None or br is None:
            overlay.clear_selection()
            return
        image_region = QRectF(
            tl,
            br
        )
        if overlay.region() == image_region:
            return
        self._renderer.overlays().clear_selection()
        self._renderer.overlays().selection.set_region(image_region)
        self._has_selection = True
        self._emit_signal("select_region", "selected_region_changed", norm_region)
        self.update()

    def clear_selection(self):
        if self._has_selection:
            self._renderer.overlays().clear_selection()
            self._has_selection = False
            self._emit_signal("clear_selection", "selection_cleared")
            self.update()

    def has_selection(self):
        return self._has_selection

    def has_selected_region(self):
        return self._has_selection and self._renderer.overlays().selection is not None

    def selected_region(self):
        if not self.has_selected_region():
            return None
        return self._renderer.overlays().selection.int_region()

    def selected_region_image(self):
        if self.pixviz() is None:
            return None
        image = self.pixviz().image()
        if image is None:
            return None
        region = self.selected_region()
        if region is not None:
            image = image[region.y():region.y() + region.height(), region.x():region.x() + region.width(), ...]
        return image

    def paintEvent(self, event):
        self.__log.debug("paintEvent()")
        painter = QPainter(self)
        screen_zoom = self._renderer.screen_zoom()
        self._renderer.render(painter)
        if self._renderer.screen_zoom() != screen_zoom:
            self.zoom_changed.emit()

    def mousePressEvent(self, e):
        if self._is_outside_image(e):
            return

        if e.button() == Qt.LeftButton:
            self.__log.debug("Left button down")
            self._left_down = True

        if e.button() == Qt.MidButton:
            self.__log.debug("Middle button down")
            self._middle_down = True
            self.setCursor(Qt.ClosedHandCursor)

        self._mouse_down_pos = e.pos()
        self._last_mouse_pos = e.pos()
        self._mouse_moved = False

    def mouseMoveEvent(self, e):
        self._mouse_moved = True

        if self._is_outside_image(e):
            self._end_action()
            return

        new_pos = e.pos()
        self._last_mouse_pos = new_pos

        self._manager.update_preview_pos(new_pos)

        if self._middle_down:
            pass
        elif self._left_down:
            self.select_region(QRectF(
                self._renderer.viewport_to_norm(self._mouse_down_pos),
                self._renderer.viewport_to_norm(e.pos())
            ).normalized())
        elif not self._has_selection:
            image_pos = self._renderer.viewport_to_image(e.pos())
            self.mouse_hovered.emit(image_pos)

    def mouseReleaseEvent(self, e):
        if self._is_outside_image(e):
            return

        if e.button() == Qt.LeftButton:
            self.__log.debug("Left button up")
            self._left_down = False
            if not self._mouse_moved:
                self.select_pixel(self._renderer.viewport_to_norm(e.pos()))

        if e.button() == Qt.MidButton:
            self.__log.debug("Middle button up")
            self._middle_down = False

        self._end_action()

    def leaveEvent(self, e):
        self._end_action()

