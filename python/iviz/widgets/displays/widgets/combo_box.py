#!/usr/bin/env python3

from PyQt5.Qt import QTimer
from PyQt5.QtWidgets import QComboBox

#
# This makes sure the popup of the combo box does not
# cause the parent widget to be left.
#
class DisplayComboBox(QComboBox):
    def showPopup(self):
        super().showPopup()
        QTimer().singleShot(1, self._delayed_update_show)

    def _delayed_update_show(self):
        parent = self
        while parent is not None:
            if hasattr(parent, 'enter'):
                parent.enter()
                return
            parent = parent.parent()

