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
from .int_slider import IntSlider
from .fps_slider import FPSSlider
from PyQt5.QtWidgets import QWidget, QComboBox, QGridLayout, QPushButton, QSizePolicy
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QIcon
from ...resources import display_highlight_border_width, play_icon_file, previous_icon_file, next_icon_file


class SequenceControls(QWidget):
    index_changed = pyqtSignal(int)

    def __init__(self, dataset):
        self.__log = TraceLogger()
        super().__init__()

        self._ds = dataset
        self._index = None

        self._frame_delay = 1/5 # 5 frames per second
        self._play_timer = QTimer()
        self._play_timer.timeout.connect(self._play_next)

        self.initUI()

    def _len(self):
        return len(self._ds)
    
    def set_dataset(self, dataset):
        self._ds = dataset
        self._slider.set_range((0, self._len() - 1))

        for item in self._ds.seq.group_list():
            index = item["index"]
            label = item["label"]
            self._group_id_dropdown.addItem(label, index)

    def goto_index(self, index):
        if self._index == index: return
        self.__log.debug(f"goto index {index} (old = {self._index})")

        self._index = index

        self._slider.change_value(index)

        item = self._ds.seq.full_item_list()[self._index]
        group_label = item["group_label"]
        group_id = item["group_id"]
        self._group_id_dropdown.blockSignals(True)
        self._group_id_dropdown.setCurrentText(group_label)
        self._group_id_dropdown.blockSignals(False)

        item_label = item["item_label"]
        self._item_id_dropdown.blockSignals(True)
        self._item_id_dropdown.clear()
        for item in self._ds.seq.item_list(group_id):
            index = item["index"]
            label = item["label"]
            self._item_id_dropdown.addItem(label, index)
        self._item_id_dropdown.setCurrentText(item_label)
        self._item_id_dropdown.blockSignals(False)

        self.index_changed.emit(self._index)

    def initUI(self):
        self._layout = QGridLayout()

        self._layout.setContentsMargins(0, 0, 0, 0)

        self._group_id_dropdown = QComboBox()
        self._group_id_dropdown.currentIndexChanged.connect(self.current_group_dropdown_changed)
        self._layout.addWidget(self._group_id_dropdown, 0, 0, 1, 1)

        self._item_id_dropdown = QComboBox()
        self._item_id_dropdown.currentIndexChanged.connect(self.current_sample_dropdown_changed)
        self._layout.addWidget(self._item_id_dropdown, 0, 1, 1, 1)

        self._slider = IntSlider((0, 0))
        self._slider.value_changed.connect(self.goto_index)
        self._layout.addWidget(self._slider, 0, 2, 1, 1)
        self._layout.setColumnStretch(2, 2)

        self._play_button = QPushButton("Play")
        self._play_button.setIcon(QIcon(play_icon_file.str()))
        self._play_button.setCheckable(True)
        self._play_button.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        def play_toggle(value):
            if value: self.play()
            else: self.stop()
        self._play_button.toggled.connect(play_toggle)
        self._layout.addWidget(self._play_button, 0, 5, 1, 1)

        self._fps = FPSSlider()
        self._fps.valueChanged.connect(self._update_fps)
        self._layout.addWidget(self._fps, 0, 6, 1, 1)

        self._prev_button = QPushButton("Prev")
        self._prev_button.setIcon(QIcon(previous_icon_file.str()))
        self._prev_button.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self._prev_button.clicked.connect(self.previous)
        self._layout.addWidget(self._prev_button, 0, 3, 1, 1)

        self._next_button = QPushButton("Next")
        self._next_button.setIcon(QIcon(next_icon_file.str()))
        self._next_button.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self._next_button.clicked.connect(self.next)
        self._layout.addWidget(self._next_button, 0, 4, 1, 1)

        self.setLayout(self._layout)

        self.set_dataset(self._ds)

    def _update_fps(self, value):
        self._frame_delay = 1 / value

        if self._play_timer.isActive():
            self._play_timer.stop()
            self._play_timer.start(int(self._frame_delay * 1000))

    def next(self):
        if self._index < self._len() - 1:
            self.goto_index(self._index + 1)

    def _play_next(self):
        if self._index < self._len() - 1:
            self.goto_index(self._index + 1)

            if self._index == self._len() - 1:
                self.stop()
        else:
            self.stop()

    def play(self):
        self._play_next()
        self._play_timer.start(int(self._frame_delay * 1000))
        self._play_button.blockSignals(True)
        self._play_button.setChecked(True)
        self._play_button.blockSignals(False)

    def stop(self):
        self._play_timer.stop()
        self._play_button.blockSignals(True)
        self._play_button.setChecked(False)
        self._play_button.blockSignals(False)

    def previous(self):
        if self._index > 0:
            self.goto_index(self._index - 1)

    def current_group_dropdown_changed(self):
        index = self._group_id_dropdown.currentData()
        self.__log.debug(f"group changed index to {index}")
        self.goto_index(index)

    def current_sample_dropdown_changed(self):
        index = self._item_id_dropdown.currentData()
        self.__log.debug(f"sample changed index to {index}")
        self.goto_index(index)
