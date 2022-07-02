#!/usr/bin/env python3

from itypes import addr, TraceLogger
from ._raster import _RasterDisplay
from ..controls import FloatRangeSlider
from PyQt5.Qt import Qt, QSizePolicy, pyqtSignal, QTimer, QEvent
from PyQt5.QtWidgets import QLabel, QPushButton, QWidget, QGridLayout, QSpinBox
from PyQt5.QtGui import QPalette
from .widgets import DisplayComboBox
from ..basic import Divider
from ...resources import status_bar_color


class FloatDisplay(_RasterDisplay):
    def __init__(self, *args, **kwargs):
        self.__log = TraceLogger()
        super().__init__(*args, **kwargs)
        self.initUI()

    def initUI(self):
        self.__log.debug(f'called')
        super().initUI()

        self._controls_layout.setSpacing(2)
        self._controls_layout.setContentsMargins(0, 0, 0, 0)

        self._dim_label = QLabel()
        self._dim_label.setAlignment(Qt.AlignCenter)
        self._controls_layout.addWidget(self._dim_label, 0, 0, 1, 1)

        self._viz_type = DisplayComboBox()
        self._viz_type.addItem('HEAT')
        self._viz_type.addItem('GRAY')
        self._viz_type.addItem('RGB')
        self._controls_layout.addWidget(self._viz_type, 1, 0, 1, 1)
        self._viz_type.activated.connect(self._change_viz_type)

        self._divider1 = Divider(direction=Divider.VERTICAL, color=status_bar_color, size=2)
        self._controls_layout.addWidget(self._divider1, 0, 1, 2, 1)

        self._range_slider = FloatRangeSlider(limit=False)
        self._range_slider.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self._controls_layout.addWidget(self._range_slider, 0, 4, 2, 1)
        self._range_slider.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self._range_slider.lower_value_changed.connect(self._change_viz_range_min)
        self._range_slider.upper_value_changed.connect(self._change_viz_range_max)

        self._range_to_all_button = QPushButton("All")
        self._range_to_all_button.setFixedWidth(65)
        self._controls_layout.addWidget(self._range_to_all_button, 0, 5, 2, 1)
        self._range_to_all_button.clicked.connect(self._range_to_all)

        if self._pixviz is not None:
            self._view.set_pixviz(self._pixviz)

    def _range_to_channel(self):
        viz = self._view.pixviz()
        if viz is None: return

        data = viz.numpy_slice_data()
        min = data.min()
        max = data.max()
        self._change_viz_range_min(min)
        self._change_viz_range_max(max)

    def _range_to_all(self):
        viz = self._view.pixviz()
        if viz is None: return

        data = viz.data()
        min = data.float().data().min()
        max = data.float().data().max()
        self._change_viz_range_min(min)
        self._change_viz_range_max(max)

    def _pixviz_updated(self):
        self.__log.debug(f"called")

        viz = self._view.pixviz()

        self._viz_type.blockSignals(True)
        viz_type = viz.viz_type()
        if viz_type == 'heatmap':     self._viz_type.setCurrentText('HEAT')
        elif viz_type == 'grayscale': self._viz_type.setCurrentText('GRAY')
        else:                         self._viz_type.setCurrentText('RGB')
        self._viz_type.blockSignals(False)

        if viz.valid():
            self._range_slider.blockSignals(True)
            self._range_slider.set_range(
                viz.min_value(),
                viz.max_value()
            )
            self._range_slider.set_selection(
                viz.range_min(),
                viz.range_max()
            )
            self._range_slider.blockSignals(False)

            self._dim_label.setText(",".join([str(x) for x in viz.numpy_data().shape]))

            self._copy_path_action.setVisible(True)
        else:
            self._copy_path_action.setVisible(False)

        super()._pixviz_updated()

    def update_property(self, property, value):
        pixviz = self.view().pixviz()
        if pixviz is None: return

        if property == 'float_viz_type':
            self.__log.debug(f"property float_viz_type updated to {value}")
            pixviz.set_viz_type(value)

        if property == 'float_viz_range_min':
            self.__log.debug(f"property float_viz_range_min updated to {value}")
            pixviz.set_range_min(value)

        if property == 'float_viz_range_max':
            self.__log.debug(f"property float_viz_range_max updated to {value}")
            pixviz.set_range_max(value)

    def _change_viz_type(self, value):
        if value == 0:   type = 'heatmap'
        elif value == 1: type = 'grayscale'
        else:            type = 'rgb'

        self.__log.debug(f"broadcasting float_viz_type")
        self._manager.broadcast_property_update(self, 'float_viz_type', type)

    def _change_viz_range_min(self, value):
        self.__log.debug(f"broadcasting float_viz_range_min = {value}")
        self._manager.broadcast_property_update(self, 'float_viz_range_min', value)

    def _change_viz_range_max(self, value):
        self.__log.debug(f"broadcasting float_viz_range_max = {value}")
        self._manager.broadcast_property_update(self, 'float_viz_range_max', value)

    def _update_hover_message(self, x, y):
        viz = self._view.pixviz()
        if viz is None:
            return self.set_idle_message()

        numpy_slice_data = viz.numpy_slice_data()
        if x >= numpy_slice_data.shape[1]:
            return self.set_idle_message()
        elif y >= numpy_slice_data.shape[0]:
            return self.set_idle_message()

        coords = viz.data_index(x, y)
        if len(coords) == 1:
            coords = coords[0]
        value = viz.numpy_data()[coords]

        self.set_status_message(f"Hover: {coords}, data = {value:.2f}")

    def _update_selected_position_message(self, x, y):
        viz = self._view.pixviz()
        if viz is None:
            return self.set_idle_message()

        coords = viz.data_index(x, y)
        if len(coords) == 1:
            coords = coords[0]
        value = viz.numpy_data()[coords]

        self.set_status_message(f"Selected: {coords}, data = {value:.2f}")

    def _update_selected_region_message(self, x1, y1, x2, y2):
        viz = self._view.pixviz()
        if viz is None:
            return self.set_idle_message()

        index1 = viz.data_index(x1, y1)
        if len(index1) == 1:
            index1 = index1[0]
        index2 = viz.data_index(x2, y2)
        if len(index2) == 1:
            index2 = index2[0]

        width = x2 - x1
        height = y2 - y1

        data = viz.numpy_slice_data()[y1:y2, x1:x2, :]

        if width > 0 and height > 0:
            self.set_status_message(f'Selected: start = {index1}, end = {index2}, min = {data.min()}, max = {data.max()}, mean = {data.mean():.2f}')
        else:
            self.set_idle_message()
