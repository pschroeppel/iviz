#!/usr/bin/env python3

from ._raster import _RasterDisplay
from .widgets import DisplayComboBox
from itypes import TraceLogger
from PyQt5.QtWidgets import QSizePolicy, QLabel


class ImageDisplay(_RasterDisplay):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__log = TraceLogger()
        self.initUI()

    def initUI(self):
        super().initUI()

        self._viz_type = DisplayComboBox()
        self._viz_type.addItem('RGB')
        self._viz_type.addItem('BGR')
        self._controls_layout.addWidget(self._viz_type, 0, 0)
        self._viz_type.activated.connect(self._change_viz_type)

        self._spacer = QLabel()
        self._spacer.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Minimum)
        self._controls_layout.addWidget(self._spacer, 0, 1)

        if self._pixviz is not None:
            self._view.set_pixviz(self._pixviz)

    def _pixviz_updated(self):
        viz = self._view.pixviz()

        viz_type = viz.viz_type()
        if viz_type == 'RGB':  self._viz_type.setCurrentText('RGB')
        else:                  self._viz_type.setCurrentText('BGR')

        self._viz_type.setVisible(not viz.is_grayscale())

        self.__log.debug(f"visualization renderer updated, viz_type={viz_type}")

        super()._pixviz_updated()

    def update_property(self, property, value):
        pixviz = self.view().pixviz()
        if pixviz is None: return

        if property == 'image_viz_type':
            self.__log.debug(f"property image_viz_type updated to {value}")
            pixviz.set_viz_type(value)

    def _change_viz_type(self, value):
        if value == 0: type = 'RGB'
        else:          type = 'BGR'

        self.__log.debug(f"broadcasting image_viz_type")
        self._manager.broadcast_property_update(self, 'image_viz_type', type)

    def _update_hover_message(self, x, y):
        data = self._view.pixviz().numpy_data()
        if x < data.shape[1] and y < data.shape[0]:
            rgb = data[y, x, :]
            if len(rgb) == 3:
                self.set_status_message(f"Hover: x = {x}, y = {y}, rgb = ({rgb[0]}, {rgb[1]}, {rgb[2]})")
            else:
                self.set_status_message(f"Hover: x = {x}, y = {y}, intensity = {rgb[0]}")
        else:
            self.set_idle_message()

    def _update_selected_position_message(self, x, y):
        data = self._view.pixviz().numpy_data()
        if x < data.shape[1] and y < data.shape[0]:
            rgb = data[y, x, :]
            if len(rgb) == 3:
                self.set_status_message(f"Selected: x = {x}, y = {y}, rgb = ({rgb[0]}, {rgb[1]}, {rgb[2]})")
            else:
                self.set_status_message(f"Selected: x = {x}, y = {y}, intensity = {rgb[0]}")
        else:
            self.set_idle_message()

