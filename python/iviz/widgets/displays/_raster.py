#!/usr/bin/env python3
2
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSizePolicy, QMenu, QPushButton, QCheckBox, QAction, QApplication
from PyQt5.QtGui import QPalette
from PyQt5.QtCore import pyqtSignal, Qt, QMargins, QRect, QTimer, QSize
from ._viz import _VisualizationDisplay
from ..containers import View
from itypes import addr, TraceLogger
from ...utils import to_qpixmap, to_qimage


class _RasterDisplay(_VisualizationDisplay):
    def __init__(self, manager=None, pixviz=None, id=None, label=None):
        self.__log = TraceLogger()
        self._selected_position = None
        self._selected_region = None
        self._pixviz = pixviz
        super().__init__(manager, id, label)

    def reload(self):
        if self._view.pixviz() is not None:
            self._view.pixviz().reload()

    def _update_zoom(self):
        if self._view is not None:
            self._status.set_zoom(self._view.renderer().screen_zoom())

    def _create_context_menu(self):
        self._context_menu = QMenu(self)

        self._copy_path_action = QAction("Copy Path")
        self._copy_path_action.setWhatsThis("Copy the path of the current file")
        self._copy_path_action.triggered.connect(self.copy_path)
        self._context_menu.addAction(self._copy_path_action)

        self._copy_image = QAction("Copy Image")
        self._copy_image.setWhatsThis("Copy the image of the current visualization")
        self._copy_image.triggered.connect(self.copy_image)
        self._context_menu.addAction(self._copy_image)

        self._copy_selection = QAction("Copy Selection")
        self._copy_selection.setWhatsThis("Copy the image of the current box selection")
        self._copy_selection.triggered.connect(self.copy_selection)
        self._context_menu.addAction(self._copy_selection)

        self._reload_action = QAction("Reload")
        self._reload_action.setWhatsThis("Reload the current file")
        self._reload_action.triggered.connect(self.reload)
        self._context_menu.addAction(self._reload_action)

    def copy_image(self):
        if self._view.pixviz() is not None and self._view.pixviz().valid():
            image = self._view.pixviz().numpy_image()
            QApplication.clipboard().setPixmap(to_qpixmap(image))
        else:
            QApplication.clipboard().clear()
        self.__log.debug("called")

    def copy_selection(self):
        if self._view.pixviz() is not None and self._view.selected_region_image() is not None:
            image = self._view.selected_region_image()
            QApplication.clipboard().setPixmap(to_qpixmap(image))
        else:
            QApplication.clipboard().clear()
        self.__log.debug("called")

    def drag_and_drop_image(self):
        if self._view.pixviz() is not None and self._view.selected_region_image() is not None:
            image = self._view.selected_region_image()
            return to_qimage(image)

        if self._view.pixviz() is not None and self._view.pixviz().valid():
            image = self._view.pixviz().numpy_image()
            return to_qimage(image)

        return None

    def _create_view(self):
        self._view = View(self._manager)
        self._view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self._layout.addWidget(self._view)

        self._view.selected_pixel_changed.connect(self.select_pixel)
        self._view.selected_region_changed.connect(self.select_region)
        self._view.selection_cleared.connect(self.clear_selection)
        self._view.mouse_hovered.connect(self.hover)
        self._view.zoom_changed.connect(self._update_zoom)

        self._view.register_pixviz.connect(self._register_pixviz)
        self._view.deregister_pixviz.connect(self._deregister_pixviz)
        if self._view.pixviz() is not None:
            self._register_pixviz()

    def _register_pixviz(self):
        viz = self._view.pixviz()
        viz.changed.connect(self._pixviz_updated)
        self._pixviz_updated()

    def _deregister_pixviz(self):
        viz = self._view.pixviz()
        viz.changed.disconnect(self._pixviz_updated)

    def _pixviz_updated(self):
        self._update_contents_enabled()
        self._update_status_message()
        QTimer.singleShot(1, self._update_zoom)

        viz = self._view.pixviz()
        if viz.valid():
            self._copy_path_action.setVisible(True)
        else:
            self._copy_path_action.setVisible(False)

        var_id = None
        if viz.valid():
            var_id = self._view.pixviz().data().var_id()

        self._update_source_info(var_id, self._view.pixviz().file())

    def is_valid(self):
        if self._view.pixviz() is None or not self._view.pixviz().valid():
            return False
        return True

    def _update_contents_enabled(self):
        invalid = not self.is_valid()
        fade = self._faded

        if invalid or fade:
            self._copy_path_action.setEnabled(False)
            self._copy_image.setEnabled(False)
            self._copy_selection.setEnabled(False)
        else:
            self._copy_path_action.setEnabled(True)
            self._copy_image.setEnabled(True)
            self._copy_selection.setEnabled(self._selected_region is not None)

        self._label_widget.setEnabled(not fade)
        self._head_widget.setEnabled(not fade)
        self._status.setEnabled(not fade)
        self._controls.setEnabled(not fade and not invalid)
        self._view.setEnabled(not fade and not invalid)

    def hover(self, image_point):
        if self._selected_position is not None:
            return
        if self._selected_region is not None:
            return
        if image_point is None or image_point.isNull():
            return self.set_idle_message()
        self._update_hover_message(int(image_point.x()), int(image_point.y()))

    def view(self): return self._view
    def image(self): raise NotImplementedError

    def set_zoom(self, screen_zoom):
        self._status.set_zoom(screen_zoom)

    def _update_hover_message(self, x, y):
        self.set_status_message(f"Hover: x = {x}, y = {y}")

    def _update_selected_region_message(self, x1, y1, x2, y2):
        width = x2 - x1
        height = y2 - y1

        data = self._view.pixviz().numpy_data()[y1:y2, x1:x2, :]

        if width > 0 and height > 0:
            self.set_status_message(
                f'Selected: tl = ({x1}, {y1}), br = ({x2}, {y2}), width = {width}, height = {height}, min = {data.min()}, max = {data.max()}, mean = {data.mean():.2f}')
        else:
            self.set_idle_message()

    def set_data(self, data):
        self.view().pixviz().set_data(data)

    def _update_selected_position_message(self, x, y):
        pass

    def _update_status_message(self):
        self.__log.trace(f'called')

        viz = self._view.pixviz()
        if viz is None:
            return self.set_idle_message()

        data = viz.numpy_slice_data()
        if data is None:
            return self.set_idle_message()

        if self._selected_position is not None:
            x = int(self._selected_position.x())
            y = int(self._selected_position.y())
            if x < 0 or x >= data.shape[1] or y < 0 or y >= data.shape[0]:
                return self.set_idle_message()
            return self._update_selected_position_message(x, y)

        if self._selected_region is not None:
            x1 = int(self._selected_region.topLeft().x())
            y1 = int(self._selected_region.topLeft().y())
            if x1 < 0 or x1 >= data.shape[1] or y1 < 0 or y1 >= data.shape[0]:
                return self.set_idle_message()
            x2 = int(self._selected_region.bottomRight().x() + 1)
            y2 = int(self._selected_region.bottomRight().y() + 1)
            if x2 < 0 or x2 >= data.shape[1] or y2 < 0 or y2 >= data.shape[0]:
                return self.set_idle_message()
            return self._update_selected_region_message(x1, y1, x2, y2)

        return self.set_idle_message()

    def select_pixel(self, norm_pos):
        self._selected_region = None
        self._selected_position = self._view.renderer().norm_to_image(norm_pos)
        self._update_status_message()

    def select_region(self, norm_rect):
        self._selected_position = None
        int_region = self._view.renderer().overlays().selection.int_region()
        if int_region is not None:
            self._selected_region = int_region
            self._copy_selection.setEnabled(True)
        else:
            self._copy_selection.setEnabled(False)
        self._update_status_message()

    def clear_selection(self):
        self.__log.debug(f'called')
        self._selected_position = None
        self._selected_region = None
        self._copy_selection.setEnabled(False)
        self._update_status_message()

    def set_idle_message(self):
        self.__log.trace(f'called')

        if self._view.pixviz() is None:
            self.set_status_message("Invalid")
            return

        data = self._view.pixviz().numpy_data()
        if data is None:
            self.set_status_message("Invalid")
            return

        shape_str = " x ".join([str(x) for x in data.shape])
        self.set_status_message(f"Data size is {shape_str}")


