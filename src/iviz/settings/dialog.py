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
from itypes import Path, TraceLogger


class SettingsDialog(QDialog):
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



