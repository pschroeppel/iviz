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

from itypes import addr, TraceLogger
from math import pow
from itypes import bind_to_instance
from PyQt5.QtCore import QObject
from PyQt5.QtCore import pyqtSignal, Qt, QSize, QPoint, QPointF, QRect, QRectF
from copy import copy


class Manager(QObject):
    previewing_changed = pyqtSignal()

    def __init__(self):
        self.__log = TraceLogger()
        super().__init__()
        self._modifiers = set()
        self._current_group = None
        self._current_display = None
        self._displays = []
        self._groups = {}
        self._preview_widget_pos = None
        self._linear_preview_zoom = 4
        for group_name in ["S", "1", "2", "3", "4", "5"]:
            self._groups[group_name] = set()

    def preview_widget_pos(self): return self._preview_widget_pos

    def preview_zoom(self):
        return pow(1.1, self._linear_preview_zoom)

    def register_display(self, display):
        self._displays.append(display)

    def turn_on_modifier(self, modifier):
        if modifier not in self._modifiers:
            self._modifiers.add(modifier)
            self.__log.debug(f'modifier {modifier} turned on, current_display={self._current_display}, current_group={self._current_group}')
            if modifier == "preview":
                self.previewing_changed.emit()
            self._highlight_displays()

    def turn_off_modifier(self, modifier):
        if modifier in self._modifiers:
            self._modifiers.remove(modifier)
            self.__log.debug(f'modifier {modifier} turned off, current_display={self._current_display}, current_group={self._current_group}')
            if modifier == "preview":
                self.previewing_changed.emit()
            self._highlight_displays()

    def clear_modifiers(self):
        modifiers = copy(self._modifiers)
        for modifier in modifiers:
            self.turn_off_modifier(modifier)

    def join_group(self, display, group):
        if display not in self._groups[group]:
            self._groups[group].add(display)

    def leave_group(self, display, group):
        self._groups[group].remove(display)

    def active_groups(self):
        result = []
        for group_name, displays in self._groups.items():
            if len(displays):
                result.append(group_name)
        return result

    def modifier_state(self, modifier):
        return modifier in self._modifiers

    def _highlight_displays(self):
        displays = self._displays
        selected_displays = self.selected_displays()
        for display in displays:
            display.set_highlighted(display in selected_displays)
            if not display in selected_displays and self.modifier_state('group'):
                display.set_faded(True)
            else:
                display.set_faded(False)

    def set_current_display(self, display):
        if self._current_display != display:
            self.__log.debug(f"current_display = {addr(display)}")
            self._current_display = display
            self._highlight_displays()

    def set_current_group(self, group):
        self.__log.debug("current group set to %s" % group)
        self._current_group = group
        self._highlight_displays()

    def selected_displays(self):
        if 'all' in self._modifiers:
            return self._displays
        elif 'group' in self._modifiers and self._current_group is not None:
            return list(self._groups[self._current_group])
        elif self._current_display is not None:
            return [self._current_display]
        return []

    def no_selection(self):
        return len(self.selected_displays()) == 0

    def update_preview_pos(self, widget_pos):
        if self._preview_widget_pos == widget_pos:
            return
        self._preview_widget_pos = widget_pos
        if self.modifier_state("preview"):
            self.previewing_changed.emit()

    def increase_preview_zoom(self):
        self._linear_preview_zoom += 1
        if self.modifier_state("preview"):
            self.previewing_changed.emit()

    def decrease_preview_zoom(self):
        self._linear_preview_zoom -= 1
        if self.modifier_state("preview"):
            self.previewing_changed.emit()

    relative_zoom_set = pyqtSignal(float, QPointF)
    def set_relative_zoom(self, value, pos):
        for display in self.selected_displays():
            if not hasattr(display, 'view'): continue
            display.view().set_relative_zoom(value, pos)
        self.relative_zoom_set.emit(value, pos)

    def broadcast_differential_relative_zoom(self, value, pos):
        for display in self.selected_displays():
            if not hasattr(display, 'view'): continue
            if display != self._current_display:
                display.view().differential_relative_zoom(value, pos)

    screen_zoom_set = pyqtSignal(float, QPointF)
    def set_screen_zoom(self, value, pos):
        for display in self.selected_displays():
            if not hasattr(display, 'view'): continue
            display.view().set_screen_zoom(value, pos)
        self.screen_zoom_set.emit(value, pos)

    pan_offset_set = pyqtSignal(QPoint)
    def set_pan_offset(self, value):
        for display in self.selected_displays():
            if not hasattr(display, 'view'): continue
            display.view().set_pan_offset(value)
        self.pan_offset_set.emit(value)

    def broadcast_differential_pan_offset(self, value):
        for display in self.selected_displays():
            if not hasattr(display, 'view'): continue
            if display != self._current_display:
                display.view().differential_pan_offset(value)

    selected_pixel_changed = pyqtSignal(QPointF)
    def select_pixel(self, value):
        for display in self.selected_displays():
            if not hasattr(display, 'view'): continue
            display.view().select_pixel(value)
        self.selected_pixel_changed.emit(value)

    selected_region_changed = pyqtSignal(QRectF)
    def select_region(self, value):
        for display in self.selected_displays():
            if not hasattr(display, 'view'): continue
            display.view().select_region(value)
        self.selected_region_changed.emit(value)

    selection_cleared = pyqtSignal()
    def clear_selection(self):
        for display in self.selected_displays():
            if not hasattr(display, 'view'): continue
            display.view().clear_selection()
        self.selection_cleared.emit()

    def set_interpolation(self, value):
        for display in self._displays:
            if not hasattr(display, 'view'): continue
            display.view().set_interpolation(value)

    def zoom_to_selection(self):
        for display in self.selected_displays():
            if not hasattr(display, 'view'): continue
            display.view().zoom_to_selection()

    def broadcast_property_update(self, sender, property, value):
        sender.update_property(property, value)
        for display in self.selected_displays():
            if not hasattr(display, 'view'): continue
            if display == sender:
                continue
            display.update_property(property, value)
