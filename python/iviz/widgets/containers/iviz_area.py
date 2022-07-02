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

from itypes import Struct, addr, TraceLogger
from PyQt5.QtGui import QCursor, QPainter, QColor, QPixmap, QKeyEvent, QPalette
from PyQt5.QtWidgets import QGridLayout, QWidget, QApplication
from PyQt5.QtWidgets import QMenuBar, QAction, QMenu, QSizePolicy
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import Qt, QPointF, QRect, QEvent, QObject
from ...utils import qpixmap_to_numpy
from PyQt5.QtWidgets import QFileDialog
from ..dialogs import SaveViewsDialog
from ..basic import Divider
from ...resources import display_highlight_border_width, display_grid_spacing

# Modifier keys:
# Space or shift = preview
# CTRL = All views
# Alt = Current group


class GroupMenu(QMenu):
    def keyReleaseEvent(self, e):
        if not (e.modifiers() & Qt.ALT):
            self.close()
        else:
            return super().keyReleaseEvent(e)


def debug_event_str(object, event):
    key = event.key()
    auto_rep = event.isAutoRepeat()
    text = event.text()
    count = event.count()

    str = ""
    str += f"key={key} ({hex(key)}, auto_rep={auto_rep}, text={text} {type(text)} {[hex(ord(x)) for x in text]}, count={count}, modifiers={int(event.modifiers())}"
    str += f", KeyPress={event.type() == QEvent.KeyPress}, KeyRelease={event.type() == QEvent.KeyRelease}"
    str += f", CtrlMod={bool(event.modifiers() & Qt.ControlModifier)}"
    str += f", AltMod={bool(event.modifiers() & Qt.AltModifier)}"
    str += f", addr={addr(event)} ({type(event)}), to={addr(object)} ({type(object)})"
    return str


class EventFilter(QObject):
    def find_iviz_area(self, pointer):
        while pointer is not None:
            if isinstance(pointer, IVizArea):
                return pointer
            pointer = pointer.parent()
        return  None

    def eventFilter(self, object, event):
        if hasattr(event, "reposted"):
            assert(bool(event.modifiers() & Qt.ControlModifier) == False)
            return False

        if event.type() == QEvent.KeyPress or event.type() == QEvent.KeyRelease:
            iviz_area = self.find_iviz_area(object)
            if iviz_area is None:
                return False

            iviz_area.set_modifiers(event.modifiers())

            key = event.key()
            if key in [0, 16777249, 16777251]:
                return True
            auto_rep = event.isAutoRepeat()
            native_scan_code = event.nativeScanCode()
            native_virtual_key = event.nativeVirtualKey()
            native_modifiers = event.nativeModifiers()
            if key < 256: text = chr(key)
            else:         text = event.text()
            count = event.count()
            modifier = Qt.ShiftModifier if event.modifiers() & Qt.ShiftModifier else Qt.NoModifier
            new_event = QKeyEvent(event.type(), key, modifier, native_scan_code, native_virtual_key, native_modifiers, text, auto_rep, count)
            new_event.reposted = True
            QApplication.instance().sendEvent(object, new_event)
            return True

        return False


class PreviewOverlay(QWidget):
    def __init__(self, manager):
        self._manager = manager
        self._manager.previewing_changed.connect(self.update_previews)
        self._preview_widget_pos = None
        super().__init__()
        self.setAttribute(Qt.WA_TransparentForMouseEvents)

    def update_previews(self):
        widget_pos = self._manager.preview_widget_pos()
        enabled = self._manager.modifier_state("preview")
        if enabled and not widget_pos.isNull():
            if self._preview_widget_pos is None:
                QApplication.setOverrideCursor(QCursor(Qt.BlankCursor))
            self._preview_widget_pos = widget_pos
            self.update()
        else:
            if self._preview_widget_pos is not None:
                QApplication.restoreOverrideCursor()
            self._preview_widget_pos = None
            self.update()

    def paintEvent(self, e):
        super().paintEvent(e)

        if self._preview_widget_pos is None:
            return

        painter = QPainter(self)
        for display in self._manager.selected_displays():
            if not hasattr(display, 'view'):
                continue

            # Get view and size
            view = display.view()
            size = int(min(view.height(), view.width()) * 0.65)
            w = size
            h = size

            # Get global position
            global_pos = view.mapToGlobal(self._preview_widget_pos)

            # Get position local to overlay
            local_point = self.mapFromGlobal(global_pos)

            # Generate preview
            preview = view.preview(
                view.mapFromGlobal(global_pos),
                zoom=self._manager.preview_zoom(),
                height=h,
                width=w
            )
            if preview is None:
                continue

            # Draw the preview
            rect = QRect(int(local_point.x()-w/2), int(local_point.y()-h/2), int(w), int(h))
            painter.drawPixmap(rect, preview)

            # Draw crosshair overlay
            overlay = QPixmap(rect.width(), rect.height())
            ov_painter = QPainter()
            ov_painter.begin(overlay)
            ov_painter.setPen(QColor(0x55, 0x55, 0x55))
            ov_painter.fillRect(overlay.rect(), Qt.black)
            x = overlay.rect().width()//2
            y = overlay.rect().height()//2
            ov_painter.drawLine(x, 0, x, overlay.rect().height() - 1)
            ov_painter.drawLine(0, y, overlay.rect().width() - 1, y)
            ov_painter.end()

            old_mode = painter.compositionMode()
            painter.setCompositionMode(QPainter.RasterOp_SourceXorDestination)
            painter.drawPixmap(rect, overlay)
            painter.setCompositionMode(old_mode)

            # Draw outline
            painter.drawRect(rect)

    def preview_for_display(self, display):
        if not hasattr(display, 'view'):
            return None
        if self._preview_widget_pos is None:
            return None

        # Get view and size
        view = display.view()
        size = int(min(view.height(), view.width()) * 0.65)
        w = size
        h = size

        # Get global position
        global_pos = view.mapToGlobal(self._preview_widget_pos)

        # Generate preview
        preview = view.preview(
            view.mapFromGlobal(global_pos),
            zoom=self._manager.preview_zoom(),
            height=h,
            width=w
        )

        return preview

_event_filter = None

class IVizArea(QWidget):
    def __init__(self, manager, menu_bar=True):
        self.__log = TraceLogger()

        global _event_filter
        if _event_filter is None:
            app = QApplication.instance()
            _event_filter = EventFilter()
            app.installEventFilter(_event_filter)

        self._manager = manager
        self._has_menu_bar = menu_bar
        self._main_widget = None
        self._controls = None
        self._actions = Struct()
        self._temp_selection = False
        super().__init__()
        self.initUI()

    def initUI(self):
        self._outer_lay = QGridLayout(self)
        self._outer_lay.setSpacing(0)
        self._outer_lay.setContentsMargins(0, 0, 0, 0)

        if self._has_menu_bar:
            self._menu_bar = QMenuBar(self)
            self._menu_bar.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            self._outer_lay.addWidget(self._menu_bar)
            file = self._menu_bar.addMenu("File")
            view = self._menu_bar.addMenu("View")
            selection = self._menu_bar.addMenu("Selection")
        else:
            self._menu_bar = None

        self._actions.save_views = QAction("Save Views")
        self._actions.save_views.setShortcut("s")
        self._actions.save_views.setWhatsThis("Save views")
        self._actions.save_views.triggered.connect(self.save_views)
        if self._has_menu_bar:
            file.addAction(self._actions.save_views)

        self._actions.reload_views = QAction("Reload")
        self._actions.reload_views.setShortcut("F5")
        self._actions.reload_views.setWhatsThis("Reload views")
        self._actions.reload_views.triggered.connect(self.reload_views)
        if self._has_menu_bar:
            file.addAction(self._actions.reload_views)

        self._actions.enable_interpolation = QAction("Enable Interpolation")
        self._actions.enable_interpolation.setShortcut("F4")
        self._actions.enable_interpolation.setWhatsThis("Use smooth interpolation when resampling to zooms different than 100%")
        self._actions.enable_interpolation.setCheckable(True)
        self._actions.enable_interpolation.setChecked(True)
        self._actions.enable_interpolation.triggered.connect(self.set_interpolation)
        if self._has_menu_bar:
            view.addAction(self._actions.enable_interpolation)

        self._actions.show_display_controls = QAction("Show Widget Controls")
        self._actions.show_display_controls.setCheckable(True)
        self._actions.show_display_controls.setChecked(True)
        self._actions.show_display_controls.setWhatsThis("Show widget controls")
        self._actions.show_display_controls.toggled.connect(self.set_show_display_controls)
        if self._has_menu_bar:
            view.addAction(self._actions.show_display_controls)

        self._actions.show_sequence_controls = QAction("Show Sequence Controls")
        self._actions.show_sequence_controls.setCheckable(True)
        self._actions.show_sequence_controls.setChecked(True)
        self._actions.show_sequence_controls.setWhatsThis("Show sequence controls")
        self._actions.show_sequence_controls.toggled.connect(self.set_show_sequence_controls)
        if self._has_menu_bar:
            view.addAction(self._actions.show_sequence_controls)

        self._actions.toggle_sequence_controls = QAction("Toggle All Controls")
        self._actions.toggle_sequence_controls.setShortcut("F9")
        self._actions.toggle_sequence_controls.setWhatsThis("Toggle sequence controls")
        self._actions.toggle_sequence_controls.triggered.connect(self.toggle_sequence_controls)
        if self._has_menu_bar:
            view.addAction(self._actions.toggle_sequence_controls)

        self._actions.clear_selection = QAction("Clear")
        self._actions.clear_selection.setShortcut("ESC")
        self._actions.clear_selection.setWhatsThis("Clear current selection")
        self._actions.clear_selection.triggered.connect(self.clear_selection)
        if self._has_menu_bar:
            selection.addAction(self._actions.clear_selection)

        self._actions.next_sample = QAction("Next")
        self._actions.next_sample.setShortcut("Space")
        self._actions.clear_selection.setWhatsThis("Next sample")
        def next():
            if self._controls is None: return
            self._controls.next()
        self._actions.next_sample.triggered.connect(next)
        self.addAction(self._actions.next_sample)

        self._preview_overlay = PreviewOverlay(self._manager)
        self._preview_overlay.setParent(self)

        self._divider = Divider()

        self._group_menu = GroupMenu(self)

    def save_views(self):
        # Collect data to save
        self.__log.debug('saving')
        entries = {}
        for display in self._manager.selected_displays():
            if not hasattr(display, 'view'):
                continue

            if self._manager.modifier_state("preview"):
                self.__log.debug('collecting preview')
                data = qpixmap_to_numpy(self._preview_overlay.preview_for_display(display))
            else:
                data = display.view().selected_region_image()
                self.__log.debug('collecting region or image')

            pos = display.index()
            self.__log.debug(f'id={display.id()}, pos={pos}, data={None if data is None else data.shape}')
            if data is not None:
                entries[pos] = (display.id(), data)

        if not len(entries):
            return

        dir = QFileDialog.getExistingDirectory(self, 'Save set of images')
        if dir is not None and dir != "":
            dialog = SaveViewsDialog(self, dir, entries)
            self._manager.clear_modifiers()
            dialog.exec()

    def reload_views(self):
        for display in self._main_widget.widget().displays():
            display.reload()

    def _temp_select(self):
        self._temp_selection = False
        if self._manager.no_selection():
            self._temp_selection = True
            self._manager.turn_on_modifier("all")

    def _temp_deselect(self):
        if self._temp_selection:
            self._manager.turn_off_modifier("all")
        self._temp_selection = False

    def set_show_display_controls(self, value):
        if not hasattr(self._main_widget.widget(), 'displays'):
            return
        for display in self._main_widget.widget().displays():
            display.set_show_controls(value)

    def set_show_sequence_controls(self, value):
        if self._controls is not None:
            self._divider.setHidden(not value)
            self._controls_container.setHidden(not value)

    def toggle_sequence_controls(self):
        value = True
        if not self._actions.show_display_controls.isChecked(): value = False
        if not self._actions.show_sequence_controls.isChecked(): value = False

        value = not value
        self._actions.show_display_controls.setChecked(value)
        self._actions.show_sequence_controls.setChecked(value)

    def set_interpolation(self, value):
        self._temp_select()
        self._manager.set_interpolation(value)
        self._temp_deselect()

    def clear_selection(self):
        self._temp_select()
        self._manager.clear_selection()
        self._temp_deselect()

    def set_main_widget(self, widget):
        if self._main_widget is not None:
            self._outer_lay.removeWidget(self._main_widget)
        self._outer_lay.addWidget(widget, 1, 0)
        self._main_widget = widget
        widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self._preview_overlay.raise_()

    def set_controls(self, controls):
        if controls is not None:
            self._outer_lay.removeWidget(self._controls)
        self._controls = controls
        self._outer_lay.addWidget(self._divider, 2, 0)

        self._controls_container = QWidget()
        self._control_layout = QGridLayout()
        self._control_layout.setContentsMargins(0, 0, 0, 0)
        m = display_highlight_border_width + display_grid_spacing
        self._control_layout.setContentsMargins(m, m, m, m)
        self._control_layout.addWidget(self._controls)
        self._controls_container.setLayout(self._control_layout)

        self._outer_lay.addWidget(self._controls_container, 3, 0)
        controls.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self._preview_overlay.raise_()

    def set_modifiers(self, modifiers):
        if modifiers & Qt.SHIFT: self._manager.turn_on_modifier("preview")
        if modifiers & Qt.CTRL: self._manager.turn_on_modifier("all")
        if modifiers & Qt.ALT:
            if not self._manager.modifier_state("group"):
                groups = self._manager.active_groups()
                self.__log.debug('show menu, active groups = %s' % groups)
                if len(groups) > 1:
                    # We have groups, present menu to select one
                    self._group_menu.clear()
                    self._group_menu.addSection("Select Group")
                    for group_name in groups:
                        self._group_menu.addAction(group_name)
                    action = self._group_menu.exec(QCursor.pos())
                    if action is None: return
                    self._manager.set_current_group(action.text())
                    # Turn group modifier on
                    self._manager.turn_on_modifier("group")
                elif len(groups) == 1:
                    self._manager.set_current_group(self._manager.active_groups()[0])
                    self._manager.turn_on_modifier("group")

        if not (modifiers & Qt.SHIFT): self._manager.turn_off_modifier("preview")
        if not (modifiers & Qt.CTRL): self._manager.turn_off_modifier("all")
        if not (modifiers & Qt.ALT):
            if self._manager.modifier_state("group"):
                self._manager.turn_off_modifier("group")
                self._manager.turn_off_modifier("all")

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_S:
            self.save_views()

        return super().keyPressEvent(e)

    def resizeEvent(self, e):
        super().resizeEvent(e)
        self._preview_overlay.resize(e.size())

    def enterEvent(self, e):
        self.__log.debug("called")
        super().enterEvent(e)
        e.ignore()
        self.setFocus()
