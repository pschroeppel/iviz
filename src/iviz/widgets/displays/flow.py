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

from itypes import addr, TraceLogger
from ._raster import _RasterDisplay
from ..controls import FlowScaleSlider
from .widgets import DisplayComboBox
from PyQt5.QtWidgets import QPushButton


class FlowDisplay(_RasterDisplay):
    def __init__(self, *args, **kwargs):
        self.__log = TraceLogger()
        super().__init__(*args, **kwargs)
        self.initUI()
    
    def initUI(self):
        super().initUI()

        self._viz_type = DisplayComboBox()
        self._viz_type.addItem('MID')
        self._viz_type.addItem('SIN')
        self._controls_layout.addWidget(self._viz_type, 0, 0, 2, 1)
        self._viz_type.activated.connect(self._change_viz_type)

        self._slider = FlowScaleSlider()
        self._controls_layout.addWidget(self._slider, 0, 1, 2, 1)
        self._slider.valueChanged.connect(self._change_scale)

        self._auto_button = QPushButton("Auto")
        self._auto_button.setFixedWidth(40)
        self._controls_layout.addWidget(self._auto_button, 0, 2)
        self._auto_button.clicked.connect(self._range_to_auto)

        self._max_button = QPushButton("Max")
        self._max_button.setFixedWidth(40)
        self._controls_layout.addWidget(self._max_button, 1, 2)
        self._max_button.clicked.connect(self._range_to_max)

        if self._pixviz is not None:
            self._view.set_pixviz(self._pixviz)

    def _range_to_max(self):
        pixviz = self.view().pixviz()
        if pixviz is None: return

        pixviz.range_to_max()

    def _range_to_auto(self):
        pixviz = self.view().pixviz()
        if pixviz is None: return

        pixviz.range_to_auto()

    def _pixviz_updated(self):
        viz = self._view.pixviz()

        viz_type = viz.viz_type()
        if viz_type == 'sintel':  self._viz_type.setCurrentText('SIN')
        else:                     self._viz_type.setCurrentText('MID')

        self._slider.set_value(viz.scale())

        self.__log.debug(f"visualization renderer updated, viz_type={viz_type}, scale={viz.scale()}")

        super()._pixviz_updated()

    def update_property(self, property, value):
        pixviz = self.view().pixviz()
        if pixviz is None: return

        if property == 'flow_viz_type':
            self.__log.debug(f"property flow_viz_type updated to {value}")
            pixviz.set_viz_type(value)

        if property == 'flow_scale':
            self.__log.debug(f"property flow_scale updated to {value}")
            pixviz.set_scale(value)

    def _change_viz_type(self, value):
        if value == 0: type = 'middlebury'
        else:          type = 'sintel'

        self.__log.debug(f"broadcasting flow_viz_type")
        self._manager.broadcast_property_update(self, 'flow_viz_type', type)

    def _change_scale(self, value):
        self.__log.debug(f"broadcasting flow_scale")
        self._manager.broadcast_property_update(self, 'flow_scale', value)

    def _update_hover_message(self, x, y):
        data = self._view.pixviz().numpy_data()
        if x < data.shape[1] and y < data.shape[0]:
            flow = data[y, x, :]
            self.set_status_message(f"Hover: x = {x}, y = {y}, flow = ({flow[0]:.2f}, {flow[1]:.2f})")
        else:
            self.set_idle_message()

    def _update_selected_position_message(self, x, y):
        data = self._view.pixviz().numpy_data()
        if x < data.shape[1] and y < data.shape[0]:
            flow = data[y, x, :]
            self.set_status_message(f"Selected: x = {x}, y = {y}, flow = ({flow[0]:.2f}, {flow[1]:.2f})")
        else:
            self.set_idle_message()
