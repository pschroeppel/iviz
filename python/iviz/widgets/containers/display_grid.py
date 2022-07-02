#!/usr/bin/env python3

from itypes import TraceLogger, Grid2D, Struct
from PyQt5.QtWidgets import QGridLayout, QWidget, QPushButton, QLayout, QWidgetItem
from .grid import DisplayGridLayout


class DisplayGrid(QWidget):
    class _Row:
        def __init__(self, grid, row):
            self._grid = grid
            self._row = row
            self._col = 0

        def add_widget(self, widget, colspan=1, rowspan=1):
            while self._grid.is_occupied(self._col, self._row, colspan, rowspan):
                self._col += 1
            self._grid.set_widget(widget, self._col, self._row, colspan, rowspan)
            self._col += colspan

        def skip_cell(self):
            self._col += 1

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_value, tb):
            if exc_type is None:
                return self

    def __init__(self):
        super().__init__()
        self.__log = TraceLogger()
        self._row = 0
        self._displays = []
        self.initUI()

    def initUI(self):
         self._lay = DisplayGridLayout(self)
         self.setLayout(self._lay)

    def displays(self):
        return self._displays

    def set_show_viz_controls(self, value):
        self._lay.set_show_viz_controls(value)

    def set_show_drag_and_drop_areas(self, value):
        self._lay.set_show_drag_and_drop_areas(value)

    def is_occupied(self, col, row, colspan=1, rowspan=1):
        return self._lay.is_occupied(col, row, colspan, rowspan)

    def set_widget(self, widget, col, row, colspan=1, rowspan=1):
        widget.set_index((col, row))
        self._displays.append(widget)
        self._lay.add_widget(widget, col, row, colspan, rowspan)

    def new_row(self):
        row = self._Row(self, self._row)
        self._row += 1
        return row


