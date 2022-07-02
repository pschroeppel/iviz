#!/usr/bin/env python

from itypes import Struct, clamp, addr, TraceLogger
from copy import deepcopy

from PyQt5.QtCore import Qt, QPoint, QPointF, QRectF, QRect
from PyQt5.QtGui import QPixmap, QPainter, QColor, QBrush, QPen, QTransform

from ....utils import to_qpixmap
from ....utils import print_qtransform
from ..._base import _BaseRenderer

from .overlays import Overlays
from .annotations import Annotations


class PixelVisualizationRenderer(_BaseRenderer):
    def __init__(self, pixviz=None, interpolation=True):
        super().__init__()
        self.__log = TraceLogger()
        self._pixviz = pixviz
        self._interpolation = interpolation
        self._image = None
        self._pixmap = None
        self._valid = False
        self._fade = False

        self._geometry = Struct()
        self._geometry.viewport_width = None 
        self._geometry.viewport_height = None
        self._geometry.image_height = None 
        self._geometry.image_width = None
        self._geometry.scaled_height = None
        self._geometry.scaled_width = None
        self._geometry.sx = None
        self._geometry.sy = None
        self._geometry.x0 = None
        self._geometry.y0 = None
        self._geometry.centered_x0 = None
        self._geometry.centered_y0 = None
        self._geometry.T_image_to_norm = None
        self._geometry.T_norm_to_image = None
        self._geometry.T_norm_to_viewport = None
        self._geometry.T_viewport_to_norm = None
        self._geometry.T_image_to_viewport = None
        self._geometry.T_viewport_to_image = None
        self._geometry.T_scaled_image_to_viewport = None
        self._geometry.T_viewport_to_scaled_image = None

        self._overlays = Overlays()
        self._annotations = Annotations()

    def overlays(self): return self._overlays
    def annotations(self): return self._annotations
    def pixviz(self): return self._pixviz
    def interpolation(self): return self._interpolation
    def set_pixviz(self, pixviz): self._pixviz = pixviz


    def set_interpolation(self, interpolation):
        if interpolation == self._interpolation:
            return False
        self._interpolation = interpolation
        return True

    def set_viewport_size(self, width, height):
        g = self._geometry

        # Check if we need an update 
        if width is None or height is None:
            return 
        if width == g.viewport_width and height == g.viewport_height:
            return 
        
        # Update 
        g.viewport_width = width
        g.viewport_height = height
        self._compute_geometry() 

    def update_image(self):
        g = self._geometry

        # Check if we have an image 
        if self._pixviz is None or self._pixviz.image() is None:
            self._image = None
            self._valid = False
            g.image_width = None
            g.image_height = None
            self._annotations.set_props(None)
            return None

        # Update values
        if self._image is self._pixviz.image():
            return

        self._image = self._pixviz.image()
        new_width = self._image.shape[1]
        new_height = self._image.shape[0]
        if g.image_width != new_width or g.image_height != new_height:
            g.image_width = new_width 
            g.image_height  = new_height
            self._compute_geometry()

        self.__log.debug(f"updated image {addr(self._image)}")

        props = self._pixviz.props().data()
        self._annotations.set_props(props)

        # Update pixmap
        self._pixmap = to_qpixmap(self._image)

    def render_preview(self, viewport_point, zoom, width, height):
        if not self._valid:
            return None

        # Set up painter and fill background
        pixmap = QPixmap(width, height)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.SmoothPixmapTransform, False)
        target_rect = QRectF(0, 0, width, height)
        painter.fillRect(target_rect, Qt.gray)

        # Use the zoom relative to the screen zoom
        zoom = zoom * self.screen_zoom()

        # Compute image rectangle
        image_point = self.viewport_to_image(viewport_point)
        image_x0 = image_point.x() - width/2 / zoom
        image_y0 = image_point.y() - height/2 / zoom
        source_rect = QRectF(
            image_x0,
            image_y0,
            width / zoom,
            height / zoom
        )

        # Copy the zoomed rectangle
        painter.drawPixmap(target_rect, self._pixmap, source_rect)

        # Draw annotations
        painter.scale(zoom, zoom)
        painter.translate(-image_x0, -image_y0)

        # Paint annotation
        painter.scale_coeff = 1 / zoom
        self._annotations.paint(painter)

        # # Paint overlay with XOR composition
        # self._overlays.paint(painter)
        return pixmap

    def relative_zoom(self):
        if not self._valid: return None
        return self._geometry.relative_zoom

    def screen_zoom(self):
        g = self._geometry
        if not self._valid:
            return None

        screen_zoom = g.scaled_height / g.image_height
        return screen_zoom

    def _compute_geometry(self):
        g = self._geometry
        self._valid = False

        if self._image is None:
            return
        if g.viewport_width is None or g.viewport_height is None:
            return

        # Determine new width and height
        g.sx = g.viewport_width / g.image_width
        g.sy = g.viewport_height / g.image_height
        if g.sx < g.sy:
            g.scaled_width = g.viewport_width
            g.scaled_height = int(g.sx * g.image_height + 0.5)
        else:
            g.scaled_width = int(g.sy * g.image_width + 0.5)
            g.scaled_height = g.viewport_height

        # Origin
        g.centered_x0 = (g.viewport_width - g.scaled_width) // 2
        g.centered_y0 = (g.viewport_height - g.scaled_height) // 2
        g.x0 = g.centered_x0
        g.y0 = g.centered_y0

        # Transforms 
        g.T_image_to_viewport = QTransform(
            g.scaled_width/g.image_width, 0, 
            0, g.scaled_height/g.image_height, 
            g.x0, g.y0
        )
        result = g.T_image_to_viewport.inverted()
        if not result[1]: 
            return
        g.T_viewport_to_image = result[0]

        g.T_scaled_image_to_viewport = QTransform(
            1, 0, 
            0, 1, 
            g.x0, g.y0
        )
        result = g.T_scaled_image_to_viewport.inverted()
        if not result[1]: 
            return
        g.T_viewport_to_scaled_image = result[0]

        norm_scale = QTransform(1 / g.image_width, 0, 0, 1 / g.image_height, 0, 0)
        g.T_image_to_norm = norm_scale
        result = g.T_image_to_norm.inverted()
        if not result[1]:
            return
        g.T_norm_to_image = result[0]

        g.T_viewport_to_norm = g.T_viewport_to_image * norm_scale
        result = g.T_viewport_to_norm.inverted()
        if not result[1]:
            return
        g.T_norm_to_viewport = result[0]

        self._valid = True 
        
    def paint_image(self, painter):
        painter.setRenderHint(QPainter.SmoothPixmapTransform, self._interpolation)
        pixmap = self._pixmap
        painter.drawPixmap(0, 0, pixmap)
        if self._fade:
            painter.fillRect(pixmap.rect(), QColor(150, 150, 150, 200))

    def valid(self):
        return self._valid

    def render(self, painter):
        # Update state
        g = self._geometry
        width = painter.window().width()
        height = painter.window().height()
        self.__log.debug(f"rendering {width}x{height}")
        self.set_viewport_size(width, height)
        self.update_image()

        # Fill background
        painter.fillRect(0, 0, width, height, QBrush(Qt.gray))

        # Do noting if we don't have valid geometry
        if not self._valid:
            return False

        # Operate in image coordinates
        painter.setViewport(int(g.x0), int(g.y0), int(g.scaled_width), int(g.scaled_height))
        painter.setWindow(0, 0, int(g.image_width), int(g.image_height))
        painter.scale_coeff = g.image_width / g.scaled_width

        # Paint the image
        self.paint_image(painter)

        # Paint annotation
        self._annotations.paint(painter)

        # Paint overlay with XOR composition
        self._overlays.paint(painter)

    def viewport_to_image(self, point):
        if not self._valid: return None
        return self._geometry.T_viewport_to_image.map(QPointF(point))

    def viewport_to_scaled_image(self, point):
        if not self._valid: return None
        return self._geometry.T_viewport_to_scaled_image.map(QPointF(point))

    def viewport_to_norm(self, point):
        if not self._valid: return None
        return self._geometry.T_viewport_to_norm.map(QPointF(point))

    def norm_to_image(self, point):
        if not self._valid: return None
        return self._geometry.T_norm_to_image.map(point)

    def image_to_scaled_image(self, point):
        if not self._valid: return None
        viewport_point = self._geometry.T_image_to_viewport.map(point)
        return self._geometry.T_viewport_to_scaled_image.map(viewport_point)

    def norm_to_scaled_image(self, point):
        if not self._valid: return None
        viewport_point = self._geometry.T_norm_to_viewport.map(point)
        return self._geometry.T_viewport_to_scaled_image.map(viewport_point)




