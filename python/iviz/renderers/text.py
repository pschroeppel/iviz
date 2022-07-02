#!/usr/bin/env python3

from ._base import _BaseRenderer
from PyQt5.QtGui import QTextDocument, QPainter
from PyQt5.QtCore import QSizeF


class TextRenderer(_BaseRenderer):
    def __init__(self, data, width=2048, text=""):
        super().__init__()
        self._data = None
        self._doc = QTextDocument()
        self._doc.setTextWidth(width)
        self._doc.setUndoRedoEnabled(False)
        self._text = text

        self.set_data(data)

    def set_data(self, data):
        self._data = data

        text = self._text
        if self._data is not None:
            text = self._data.text().data()

        self._doc.setHtml(text)

        width = self._doc.textWidth()
        self._doc.setTextWidth(2048)
        self._preferred_size = QSizeF(
            self._doc.idealWidth(),
            self._doc.size().height()
        )

        self._doc.setTextWidth(width)
        # print('size', self._doc.size())
        # print('idealWidth', self._doc.idealWidth())

    def preferred_size(self):
        return self._preferred_size

    def valid(self):
        return self._text is not None or (self._data is not None and self._data.text() is not None)

    def set_viewport_size(self, width, height):
        self._doc.setTextWidth(width)

    def render(self, painter):
        painter.setRenderHint(QPainter.Antialiasing, True)
        self._doc.drawContents(painter)
