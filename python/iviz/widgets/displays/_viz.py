#!/usr/bin/env python3

import math
from itypes import addr, TraceLogger
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSizePolicy, QMenu, QPushButton, QCheckBox, QGridLayout, QFrame, QLayout, QScrollArea, QAction, QApplication
from PyQt5.QtGui import QPalette, QColor, QPainter, QPen
from PyQt5.QtCore import pyqtSignal, Qt, QMargins, QRect, QPoint, QSize
from ._base import _BaseDisplay
from ...resources import display_highlight_border_width, head_bar_color, status_bar_color, display_color, display_border_color, display_highlight_color, viz_button_size, head_bar_button_size, display_border_width


class _StatusBar(QWidget):
    def __init__(self, _initUI=True):
        super().__init__()
        if _initUI:
            self.initUI()

    def initUI(self):
        lay = QHBoxLayout()
        lay.setSpacing(0)
        lay.setContentsMargins(0, 0, 0, 0)
        self.setLayout(lay)
        self.setFixedHeight(15)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setStyleSheet('background-color: %s' % status_bar_color.name())

        self._message = QLabel()
        self._message_area = QScrollArea()
        self._message_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._message_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._message_area.setWidgetResizable(True)
        self._message_area.setWidget(self._message)
        self._message_area.setFrameShape(QFrame.NoFrame)
        lay.addWidget(self._message_area)

        self._zoom = QLabel()
        self._zoom.setMaximumWidth(80)
        self._zoom.setAlignment(Qt.AlignRight)
        lay.addWidget(self._zoom)

    def set_message(self, str):
        self._message.setText(str)

    def set_zoom(self, zoom):
        if zoom is None:
            self._zoom.setText("")
            return
        zoom = zoom * 100
        exp =  round(math.log(zoom, 10) - 0.5)
        if exp > 0:     zoom_str = '%d%%' % round(zoom)
        elif exp == 0:  zoom_str = '%1.1f%%' % zoom
        else:           zoom_str = ('%1.' + str(-exp) + 'f%%') % zoom
        self._zoom.setText(zoom_str)


class _VisualizationDisplay(_BaseDisplay):
    def __init__(self, manager=None, id=None, label=None):
        self.__log = TraceLogger()
        super().__init__(manager, id, label)
        self._show_controls = True

    def _update_source_info(self, var_id, file):
        return

    def initUI(self):
        super().initUI()

        self._layout = QGridLayout()
        self._layout.setSpacing(0)
        s = display_border_width
        self._layout.setContentsMargins(s, s, s, s)

        self._label_widget = QLabel((self._id if self._label is None else self._label))
        self._label_widget.setAlignment(Qt.AlignCenter)
        self._label_widget.setStyleSheet(f'background-color: {head_bar_color.name()}; font-weight: bold')
        self._layout.addWidget(self._label_widget)

        self._spacer_widget = QWidget()
        self._spacer_widget.setStyleSheet(f'background-color: {display_border_color.name()}')
        self._spacer_widget.setFixedHeight(1)
        self._layout.addWidget(self._spacer_widget)

        self._head_layout = QHBoxLayout()

        self._head_widget = QWidget()
        self._head_widget.setStyleSheet("color: #999999; font-size: 11px")
        self._head_widget.setLayout(self._head_layout)
        self._head_layout.setContentsMargins(QMargins(0, 0, 0, 0))
        self._layout.addWidget(self._head_widget)

        self._create_view()

        self._controls = QWidget()
        self._controls.setFixedHeight(40)
        self._controls.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self._layout.addWidget(self._controls)

        self._controls_layout = QGridLayout()
        self._controls_layout.setSpacing(2)
        self._controls_layout.setContentsMargins(0, 0, 0, 0)
        self._controls.setLayout(self._controls_layout)

        self._status = _StatusBar()
        self._layout.addWidget(self._status)

        self.setLayout(self._layout)

        self._create_context_menu()

        self._update_zoom()

        self.set_highlighted(False)

    def paintEvent(self, e):
        s = display_border_width
        width = self.width()
        height = self.height()
        p = QPainter(self)
        p.fillRect(0, 0, width, height, display_border_color)
        p.fillRect(s, s, width - 2 * s, height - 2 * s, display_color)

    def _create_context_menu(self):
        self._context_menu = QMenu(self)

        self._copy_path_action = QAction("Copy Path")
        self._copy_path_action.setWhatsThis("Copy the path of the current file")
        self._copy_path_action.triggered.connect(self.copy_path)
        self._context_menu.addAction(self._copy_path_action)

        self._reload_action = QAction("Reload")
        self._reload_action.setWhatsThis("Reload the current file")
        self._reload_action.triggered.connect(self.reload)
        self._context_menu.addAction(self._reload_action)

    def reload(self):
        if self._view.pixviz() is not None:
            self._view.pixviz().reload()

    def copy_path(self):
        path = None
        if self._view.pixviz() is not None and self._view.pixviz().file() is not None:
            path = self._view.pixviz().file().str()
        QApplication.clipboard().setText(path)
        print(f"Copied to clipboard: {path}")

    def set_show_controls(self, value):
        if self._show_controls == value:
            return
        self._show_controls = value

        self._controls.setVisible(self._show_controls)
        self._head_widget.setVisible(self._show_controls)

    def _update_contents_enabled(self):
        value = False
        if self._faded:
            value = True
        self._copy_path_action.setEnabled(value)
        self._head_widget.setEnabled(not value)
        self._controls.setEnabled(not value)
        self._view.setEnabled(not value)
        self._status.setEnabled(not value)

    def execute_action(self, action):
        pass

    def contextMenuEvent(self, event):
        self.__log.debug("called")
        action = self._context_menu.exec_(self.mapToGlobal(event.pos()))
        self.execute_action(action)

    def set_status_message(self, text):
        self.__log.trace(f'text = "{text}"')
        self._status.set_message(text)

    def set_idle_message(self):
        self.set_status_message("")

    def enter(self):
        self.__log.debug("called")
        self._manager.set_current_display(self)

    def leave(self):
        self.__log.debug("called")
        self._manager.set_current_display(None)
        if not self._view.has_selection():
            self.set_idle_message()



