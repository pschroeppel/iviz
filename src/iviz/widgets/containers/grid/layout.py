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

from math import floor, ceil
from itypes import TraceLogger, Grid2D, Struct
from PyQt5.QtWidgets import QGridLayout, QWidget, QPushButton, QLayout, QWidgetItem
from PyQt5.Qt import QSizePolicy, QSize, pyqtSignal, Qt, QTimer
from PyQt5.QtGui import QIcon, QPalette, QColor, QDrag, QPixmap
from PyQt5.QtCore import QRect, QMimeData, QRect
from ....resources import display_highlight_border_width, viz_button_size, display_grid_spacing, visible_icon_file, invisible_icon_file, display_color, placeholder_size
from ...controls import VisibilityButton
from .placeholder import DisplayPlaceholder
from .container import DisplayContainer


class DisplayGridLayout(QLayout):
    def __init__(self, parent):
        super().__init__(parent)

        self.__log = TraceLogger()

        self._parent = parent

        self._container_list = []
        self._container_grid = Grid2D()
        self._placeholder_grid = Grid2D()

        self._rect = None

        self._min_size = QSize(100, 100)

        self._drag_source = None

        self._update_timer = QTimer()

    def set_drag_source(self, value):
        pass

    def drag_source(self):
        return None

    def _update_hidden(self):
        pass

    def _is_occupied(self, col, row):
        if (col, row) not in self._container_grid:
            return False
        if self._container_grid[(col, row)].is_placeholder():
            return False
        return True

    def is_occupied(self, col, row, colspan=1, rowspan=1):
        for r in range(row, row + rowspan):
            for c in range(col, col + colspan):
                if self._is_occupied(c, r):
                    return True
        return False

    def set_show_viz_controls(self, value):
        pass

    def set_show_drag_and_drop_areas(self, value):
        pass

    def _update_placeholders(self):
        for placeholder in self._placeholder_grid.values():
            placeholder.deleteLater()
        self._placeholder_grid = Grid2D()

        for r in self._container_grid.row_range():
            for c in self._container_grid.col_range():
                container = DisplayContainer(self, DisplayPlaceholder(), c, r, 1, 1)
                container.setParent(self._parent)
                self._placeholder_grid[c, r] = container

    def _add_widget(self, widget, col, row, colspan, rowspan):
        wrapper = DisplayContainer(self, widget, col, row, colspan, rowspan)
        wrapper.setParent(self._parent)
        self._container_list.append(wrapper)

        for r in range(row, row + rowspan):
            for c in range(col, col + colspan):
                self._container_grid[c, r] = wrapper

    def add_widget(self, widget, col, row, colspan, rowspan):
        self._add_widget(widget, col, row, colspan, rowspan)

        self._update_placeholders()

        self._recompute_geometry()

    def sizeHint(self):
        return self._min_size

    def minimumSize(self):
        return self._min_size

    def count(self):
        return len(self._container_list)

    def itemAt(self, index):
        if index >= self.count():
            return None
        return self._container_list[index].item()

    def takeAt(self, index):
        if index >= self.count():
            return None
        container = self.itemAt(index)
        self._container_grid.remove_values(container)
        del self._container_list[index]
        return container.item()

    def setGeometry(self, rect):
        if self._rect == rect:
            return
        self._rect = rect
        self.__log.debug(f'rect = {rect.width()} x {rect.height()}')
        QTimer.singleShot(1, self._recompute_geometry)

    def updateGeometry(self):
        self._update_timer.stop()
        self._update_timer.singleShot(1, self._recompute_geometry)

    def _recompute_geometry(self):
        rect = self._rect

        if rect is not None:
            self.__log.debug(f'rect = {rect.width()} x {rect.height()}')
        else:
            self.__log.debug(f'initial update')

        if len(self._container_list) == 0:
            return

        nr = self._container_grid.num_rows()
        nc = self._container_grid.num_cols()

        s = display_grid_spacing

        b = display_highlight_border_width
        start_x = s + b
        start_y = s + b
        if rect is not None:
            width = rect.width() - 2 * s - 2 * b
            height = rect.height() - 2 * s - 2 * b
        else:
            width = 10000
            height = 10000

        bs = viz_button_size + 2 * display_highlight_border_width
        ps = placeholder_size + 2 * display_highlight_border_width


        start_c = self._container_grid.min_col()
        start_r = self._container_grid.min_row()
        end_c = self._container_grid.max_col()
        end_r = self._container_grid.max_row()

        start_pos = {}
        end_pos = {}

        row_props = {}
        col_props = {}

        row_min_expand_height = 0
        rows_grow_height = 0
        rows_expand_count = 0
        rows_shrink_count = 0
        for r in self._container_grid.row_range():
            props = Struct()
            props.min_height = bs
            props.preferred_height = bs
            props.expand = False
            props.shrink = False
            for c in self._container_grid.col_range():
                is_container = (c, r) in self._container_grid
                if is_container:  item = self._container_grid[c, r]
                else:             item = self._placeholder_grid[c, r]
                if item.min_height() > props.min_height:
                    props.min_height = item.min_height()
                if is_container:
                    if item.expands_vertical():
                        props.expand = True
                    elif item.shrinks_vertical():
                        props.shrink = True
                        if item.preferred_height() > props.preferred_height:
                            props.preferred_height = item.preferred_height()
            if props.min_height > row_min_expand_height:
                row_min_expand_height = props.min_height
            if props.expand:
                rows_expand_count += 1
                props.shrink = False
            if props.shrink:
                rows_shrink_count += 1
                rows_grow_height += max(0, props.preferred_height - props.min_height)
            row_props[r] = props

        col_min_expand_width = 0
        cols_expand_count = 0
        cols_shrink_count = 0
        cols_grow_width = 0
        for c in self._container_grid.col_range():
            props = Struct()
            props.min_width = bs
            props.preferred_width = bs
            props.expand = False
            props.shrink = False
            for r in self._container_grid.row_range():
                is_container = (c, r) in self._container_grid
                if is_container:  item = self._container_grid[c, r]
                else:              item = self._placeholder_grid[c, r]
                if item.min_width() > props.min_width:
                    props.min_width = item.min_width()
                if is_container:
                    if item.expands_horizontal():
                        props.expand = True
                    elif item.shrinks_horizontal():
                        props.shrink = True
                        if item.preferred_width() > props.preferred_width:
                            props.preferred_width = item.preferred_width()
            if props.min_width > col_min_expand_width:
                col_min_expand_width = props.min_width
            if props.expand:
                cols_expand_count += 1
                props.shrink = False
            if props.shrink:
                cols_shrink_count += 1
                cols_grow_width += max(0, props.preferred_width - props.min_width)
            col_props[c] = props

        for props in row_props.values():
            if props.expand:    props.height = row_min_expand_height
            else:               props.height = props.min_height

        for props in col_props.values():
            if props.expand:    props.width = col_min_expand_width
            else:               props.width = props.min_width

        # Compute minimum size
        def compute_cell_sizes():
            nonlocal start_x
            nonlocal start_y
            nonlocal col_props
            nonlocal row_props

            y = start_y
            for r in self._container_grid.row_range():
                x = start_x
                for c in self._container_grid.col_range():
                    x0 = x
                    y0 = y
                    x1 = x0 + col_props[c].width - 1
                    y1 = y0 + row_props[r].height - 1
                    start_pos[c, r] = (x0, y0)
                    end_pos[c, r] = (x1, y1)
                    x = x1 + s
                y = y1 + s

        compute_cell_sizes()

        x_end, y_end = end_pos[end_c, end_r]
        x_end += s
        y_end += s
        min_size = QSize(x_end + 1, y_end + 1)
        self._min_size = min_size

        if rect is None:
            return

        # Compute free size
        free_width = rect.width() - self._min_size.width()
        free_height = rect.height() - self._min_size.height()

        # Distribute free space
        if free_width > 0 and cols_shrink_count > 0 and cols_grow_width > 0:
            if cols_grow_width > free_width:
                fraction = free_width / cols_grow_width
                for props in col_props.values():
                    if props.shrink:
                        diff = fraction*(props.preferred_width - props.width)
                        free_width -= diff
                        props.width += diff 
            else:
                for props in col_props.values():
                    if props.shrink:
                        diff = props.preferred_width - props.width
                        free_width -= diff
                        props.width = props.preferred_width

        if free_height > 0 and rows_shrink_count > 0 and rows_grow_height > 0:
            if rows_grow_height > free_height:
                fraction = free_height / rows_grow_height
                for props in row_props.values():
                    if props.shrink:
                        diff = fraction*(props.preferred_height - props.height)
                        free_height -= diff
                        props.height += diff 
            else:
                for props in row_props.values():
                    if props.shrink:
                        diff = props.preferred_height - props.height
                        free_height -= diff
                        props.height = props.preferred_height

        if free_width > 0:
            if cols_expand_count == 0:
                expansion = free_width / nc
                for props in col_props.values():
                    props.width += expansion
            else:
                expansion = free_width / cols_expand_count
                for props in col_props.values():
                    if props.expand:
                        props.width += expansion

        if free_height > 0:
            if rows_expand_count == 0:
                expansion = free_height / nr
                for props in row_props.values():
                    props.height += expansion
            else:
                expansion = free_height / rows_expand_count
                for props in row_props.values():
                    if props.expand:
                        props.height += expansion

        # Compute actual size
        compute_cell_sizes()

        containers_processed = []
        for col in self._container_grid.col_range():
            for row in self._container_grid.row_range():
                placeholder = self._placeholder_grid[col, row]

                x0, y0 = start_pos[col, row]
                x1, y1 = end_pos[col, row]
                w = x1 - x0 + 1
                h = y1 - y0 + 1

                rect = QRect(int(x0), int(y0), int(w), int(h))
                placeholder.setGeometry(rect)

                if (col, row) not in self._container_grid:
                    placeholder.show()
                    placeholder.raise_()
                else:
                    placeholder.hide()
                    container = self._container_grid[col, row]
                    if container not in containers_processed:
                        colspan, rowspan = container.span()

                        col_end = col + colspan - 1
                        row_end = row + rowspan - 1

                        x0, y0 = start_pos[col, row]
                        x1, y1 = end_pos[col_end, row_end]
                        w = x1 - x0 + 1
                        h = y1 - y0 + 1

                        rect = QRect(int(x0), int(y0), int(w), int(h))
                        container.setGeometry(rect)
                        container.show()

                        containers_processed.append(container)

        self.__log.debug("done")
