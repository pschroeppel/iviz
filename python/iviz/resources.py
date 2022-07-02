#!/usr/bin/env python3

from itypes import File, home
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtCore import QSize

viz_button_size = 18
display_highlight_border_width = 2
display_grid_spacing = 2

display_border_width = 1
display_border_color = QColor("#aaaaaa")

placeholder_size = 10

head_bar_button_size = 14

head_bar_color = QColor('#d0d0d0')
status_bar_color = QColor('#c0c0c0')

display_highlight_color = QColor("#aa0000")
display_color = QColor('#dddddd')

iviz_root = File(__file__).path().cd('../..').abs()
iviz_icons_root = iviz_root.cd('icons').abs()

previous_icon_file = iviz_icons_root.file('previous.svg')
next_icon_file = iviz_icons_root.file('next.svg')
play_icon_file = iviz_icons_root.file('play.svg')

visible_icon_file = iviz_icons_root.file('visible.svg')
invisible_icon_file = iviz_icons_root.file('invisible.svg')

settings_file = home.cd('.iviz').file('settings.json')

expanding_minimum_size = QSize(250, 150)



# Midlight  #cacaca
# Mid       #b8b8b8
# Dark      #9f9f9f
