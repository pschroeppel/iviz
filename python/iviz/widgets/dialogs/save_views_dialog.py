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

from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QGridLayout, QLabel, QLineEdit, QVBoxLayout, QWidget, QCheckBox
from PyQt5.QtCore import Qt
from ...utils import to_qpixmap
from itypes import Path, TraceLogger


class EntrySaveDisplay(QWidget):
    def __init__(self, id, data, parent=None):
        self.__log = TraceLogger()
        super().__init__(parent)
        self._id = id
        self._data = data
        self.initUI()

    def initUI(self):
        self.setStyleSheet('.QWidget { background-color: #dddddd }')

        self._container = QWidget()
        self._conatiner_layout = QGridLayout()
        self._conatiner_layout.setSpacing(0)
        self._conatiner_layout.setContentsMargins(0, 0, 0, 0)
        self._container.setLayout(self._conatiner_layout)
        self._container.setStyleSheet(".QWidget { border: 1px solid gray }")

        self._headline = QLabel(text=self._id)
        self._headline.setStyleSheet('font-weight: bold')
        self._headline.setAlignment(Qt.AlignCenter)
        self._conatiner_layout.addWidget(self._headline)

        self._label = QLabel()
        self._label.setPixmap(to_qpixmap(self._data).scaled(120, 120, Qt.KeepAspectRatio))
        self._label.setAlignment(Qt.AlignCenter)
        self._label.setStyleSheet('background-color: gray; font-weight: bold')
        self._conatiner_layout.addWidget(self._label)

        self._filename = QLineEdit()
        self._filename.setText(self._id + ".png")
        self._filename.setMinimumWidth(200)
        self._filename.setStyleSheet('margin: 5px')
        self._conatiner_layout.addWidget(self._filename)

        self._checkmark = QCheckBox()
        self._checkmark.setChecked(True)
        self._checkmark.toggled.connect(self.toggle)

        self._layout = QGridLayout()
        self._layout.addWidget(self._checkmark, 0, 0, Qt.AlignTop)
        self._layout.addWidget(self._container, 0, 1)
        self.setLayout(self._layout)

        self._disabled_overlay = QLabel()
        self._disabled_overlay.setParent(self._container)
        self._disabled_overlay.setVisible(False)
        self._disabled_overlay.setStyleSheet('background-color: rgba(0, 0, 0, 0.5)')


    def toggle(self, value):
        self.__self.__log.debug(f'toggle {self._id} to {value}')
        self._disabled_overlay.setVisible(not value)

    def save(self, dir):
        if not self._checkmark.checkState():
            self.__self.__log.debug(f"skipping {self._id}")
            return

        self.__log.debug(f"saving {dir.file(self._filename.text())}")
        dir.file(self._filename.text()).write(self._data, dims="hwc")


class SaveViewsDialog(QDialog):
    def __init__(self, parent, dir, entries):
        self.__log = TraceLogger()
        super().__init__(parent)
        self._dir = Path(dir)

        self.setWindowTitle("Select Filenames")

        self._top_layout = QVBoxLayout()
        self.setLayout(self._top_layout)

        self._grid_layout = QGridLayout()
        self._gridWidget = QWidget()
        self._gridWidget.setLayout(self._grid_layout)
        self._top_layout.addWidget(self._gridWidget)

        q_btn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        self._button_box = QDialogButtonBox(q_btn)
        self._button_box.accepted.connect(self.accept)
        self._button_box.rejected.connect(self.reject)
        self._top_layout.addWidget(self._button_box)

        self._entry_widgets = []
        for (col, row), (id, data) in entries.items():
            widget = EntrySaveDisplay(id, data)
            self._grid_layout.addWidget(widget, row, col)
            self._entry_widgets.append(widget)

    def accept(self):
        self.__log.debug("accepted")
        
        for widget in self._entry_widgets:
            widget.save(self._dir)

        super().accept()



