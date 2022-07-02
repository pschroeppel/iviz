#!/usr/bin/env python3

from itypes import TraceLogger, File, home
from PyQt5.QtWidgets import QGridLayout, QWidget, QPushButton, QLayout, QWidgetItem, QLabel
from PyQt5.Qt import QSizePolicy, QSize, pyqtSignal, Qt, QSize
from PyQt5.QtGui import QIcon, QPalette, QColor, QDrag, QPixmap, QPainter
from PyQt5.QtCore import QRect, QMimeData, QByteArray, QBuffer, QIODevice, QUrl
from .placeholder import DisplayPlaceholder
from ....resources import display_highlight_border_width, viz_button_size, display_color, expanding_minimum_size, display_highlight_color
from ...controls import VisibilityButton
import tempfile

tmp_image_file = home.file("iviz_clipboard.png")


class DisplayContainer(QWidget):
    def __init__(self, grid, display, col, row, colspan=1, rowspan=1):
        super().__init__()
        self.__log = TraceLogger()
        self._grid = grid
        self._index = (col, row)
        self._display = display
        self._span = (colspan, rowspan)

        display.setParent(self)
        display.set_index(self._index)
        display.show()
        self._display = display

        self.setAcceptDrops(True)

        self._item = QWidgetItem(self)

        self._highlighted = False

        self._can_accept_drag = False
        self._drag_highlighted = False

        self._hidden_completely = False
        self._hidden_internally = False

        self.initUI()

    def initUI(self):
        self._lay = QGridLayout()
        self._lay.setSpacing(0)
        s = display_highlight_border_width
        self._lay.setContentsMargins(s, s, s, s)
        self._lay.addWidget(self._display)
        self.setLayout(self._lay)

        self._overlay = QWidget()
        self._overlay.setParent(self)
        self._overlay.hide()

        if not self.is_placeholder():
            self._internal_viz_button = VisibilityButton()

            self._hidden_id_label  = QLabel(self._display.id())
            self._hidden_id_label.setStyleSheet("font-weight: bold; padding: 5px")
            self._hidden_id_label.setAlignment(Qt.AlignCenter)
            self._hidden_id_label.hide()
            self._lay.addWidget(self._hidden_id_label)

            self._internal_viz_button = VisibilityButton()
            self._internal_viz_button.setVisible(False)
            self._internal_viz_button.setParent(self)
            def set_viz_internally(x):
                self.set_hide_internally(not x)
            self._internal_viz_button.toggled.connect(set_viz_internally)

    def _show_internal_viz_button(self):
        self._internal_viz_button.blockSignals(True)
        self._internal_viz_button.setChecked(not self._hidden_internally)
        self._internal_viz_button.blockSignals(False)
        s = viz_button_size + 2 * display_highlight_border_width
        w = self.width()
        h = self.height()
        padding = 2
        self._internal_viz_button.setGeometry(QRect(
            w - s - padding,
            padding,
            s,
            s
        ))
        self._internal_viz_button.show()
        self._internal_viz_button.raise_()

    def _hide_internal_viz_button(self):
        self._internal_viz_button.hide()

    def set_hide_completely(self, value):
        if self._hidden_completely == value:
            return
        self._hidden_completely = value
        self._update_hidden()

    def set_hide_internally(self, value):
        if self._hidden_internally == value:
            return
        self._hidden_internally = value
        self._update_hidden()
        if value:
            self._show_internal_viz_button()

    def _update_hidden(self):
        self._internal_viz_button.blockSignals(True)
        self._internal_viz_button.setChecked(not self._hidden_internally)
        self._internal_viz_button.blockSignals(False)

        if self._hidden_completely:
            self._display.hide()
            self._hidden_id_label.hide()
        elif self._hidden_internally:
            self._display.hide()
            self._hidden_id_label.show()
        else:
            self._display.show()
            self._hidden_id_label.hide()

    def updateGeometry(self):
        super().updateGeometry()
        self._grid.updateGeometry()

    def display(self):
        return self._display

    def set_index(self, pos):
        self._index = pos
        self._display.set_index(pos)

    def index(self):
        return self._index

    def span(self):
        return self._span

    def col_range(self):
        return range(self._index[0], self._index[0] + self._span[0])

    def row_range(self):
        return range(self._index[1], self._index[1] + self._span[1])

    def is_hidden(self):
        return self._hidden_completely or self._hidden_internally

    def reference_in(self, grid):
        for c in self.col_range():
            for r in self.row_range():
                grid[c, r] = self

    def item(self):
        return self._item

    def is_placeholder(self):
        if isinstance(self._display, DisplayPlaceholder):
            return True
        return False

    def min_height(self):
        if self._hidden_completely:
            return 0
        elif self._hidden_internally:
            return self._hidden_id_label.minimumSizeHint().height() + 2*display_highlight_border_width
        else:
            return self._display.minimumHeight() + 2*display_highlight_border_width

    def min_width(self):
        if self._hidden_completely:
            return 0
        elif self._hidden_internally:
            return self._hidden_id_label.minimumSizeHint().width() + 2*display_highlight_border_width
        else:
            return self._display.minimumWidth() + 2*display_highlight_border_width

    def expands_horizontal(self):
        if self.is_hidden():
            return False
        return self._display.sizePolicy().horizontalPolicy() == QSizePolicy.MinimumExpanding

    def expands_vertical(self):
        if self.is_hidden():
            return False
        return self._display.sizePolicy().verticalPolicy() == QSizePolicy.MinimumExpanding

    def shrinks_horizontal(self):
        if self.is_hidden():
            return True
        return self._display.sizePolicy().horizontalPolicy() == QSizePolicy.Minimum

    def shrinks_vertical(self):
        if self.is_hidden():
            return True
        return self._display.sizePolicy().verticalPolicy() == QSizePolicy.Minimum

    def preferred_height(self):
        return self.sizeHint().height()

    def preferred_width(self):
        return self.sizeHint().width()

    def paintEvent(self, e):
        s = display_highlight_border_width
        width = self.width()
        height = self.height()
        p = QPainter(self)
        p.fillRect(0, 0, width, height, QPalette().color(QPalette.Background))
        if self._highlighted: # and not (self._hidden_internally or self._hidden_completely):
            p.fillRect(0, 0, width, height, display_highlight_color)
        p.fillRect(s, s, width - 2 * s, height - 2 * s, display_color)

    def set_highlighted(self, value):
        if self._highlighted == value:
            return
        self.__log.debug(f'value = {value}')
        self._highlighted = value
        self.update()

    def enterEvent(self, e):
        if not self.is_placeholder():
            if not self._hidden_completely:
                self._show_internal_viz_button()
            if not self.is_hidden():
                self._display.enter()
        return super().enterEvent(e)

    def leaveEvent(self, e):
        if not self.is_placeholder():
            self._hide_internal_viz_button()
            if not self.is_hidden():
                self._display.leave()
        return super().leaveEvent(e)

    def mouseMoveEvent(self, e):
        if not self.is_placeholder():
            if not self.is_hidden():
                self._display.enter()
        super().mouseMoveEvent(e)

    def mousePressEvent(self, event):
        if self.is_placeholder() or event.button() != Qt.LeftButton:
            return super().mousePressEvent(event)

        self.__log.debug(f'starting to drag source_index={self._index}')
        self._grid.set_drag_source(self)

        data = QMimeData()

        image = self._display.drag_and_drop_image()
        if image is not None:
            image.save(str(tmp_image_file))
            data.setUrls([QUrl("file://" + str(tmp_image_file))])

        drag = QDrag(self)
        drag.setMimeData(data)
        pixmap = QPixmap(self.size())
        self.render(pixmap)
        drag.setPixmap(pixmap)
        drag.exec(Qt.CopyAction)
        event.accept()

    def resizeEvent(self, e):
        super().resizeEvent(e)
        self._overlay.resize(e.size())
