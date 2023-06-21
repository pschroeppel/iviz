#!/usr/bin/env python3

import abc
from pprint import pprint

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QComboBox, QGridLayout, QPushButton, QSizePolicy, QLabel
from PyQt5.QtCore import QTimer
from itypes import Dataset, Path, File, TraceLogger, is_list

from .dataset import _OversizeScrollArea


class CustomDataAdapter(metaclass=abc.ABCMeta):
    # provides data
    # knows length of the datasets
    # can provide sequence information
    # knows arrangement of cells in the grid
    # can have different layouts
    def __init__(self):
        self._displays = {}  # display: has a position x,y, a widget type, and a load_content function

    @abc.abstractmethod
    def get_displays(self, manager):
        return

    @property
    @abc.abstractmethod
    def num_items(self):
        """Returns the number of items in the dataset."""
        return

    @abc.abstractmethod
    def __getitem__(self, index):
        """Returns the data for the given index."""
        return

    def __len__(self):
        return self.num_items


class CustomDataViewer(QWidget):
    def __init__(self, controller, title=None, parent=None):
        self.__log = TraceLogger()
        super().__init__(parent)

        self._controller = controller
        self._index = -1  # TODO: set to None?
        # TODO: self._displays = {}
        self._grid = None

        if title is not None:
            title = title if title.startswith("iviz") else f"iviz: {title}"
            self.setWindowTitle(title)
        else:
            self.setWindowTitle("iviz")

        self.last_positions = []
        self.initUI()

    def initUI(self):
        self._manager = Manager()

        self._grid = DisplayGrid()
        # TODO: ask the controller for the displays (e.g. mapping from x, y to a certain widget/display)
        # for (col, row), display in self._controller.displays.items():  # TODO: provide self._manager
        #     self._grid.setWidget(col, row, display)
        # for viz in self._ds.viz:
        #     col, row = viz.index()
        #     display = viz.create_display(self._manager)
        #     self._grid.set_widget(
        #         display,
        #         col,
        #         row,
        #         colspan=viz.colspan(),
        #         rowspan=viz.rowspan()
        #     )
        #     self._displays[display.id()] = display

        self._controls = SequenceControls(self._ds)  # TODO: replace with IndexControls and do not supply dataset
        self._controls.index_changed.connect(self.change_index)

        self._grid_scroll = _OversizeScrollArea(self._grid)

        self._area = IVizArea(self._manager)
        self._area.set_main_widget(self._grid_scroll)
        self._area.set_controls(self._controls)

        # if len(self._ds.viz.ids()) == 1:  # TODO: remove or fix
        #     self._area.set_show_drag_and_drop_areas(False)
        #     self._area.set_show_viz_controls(False)

        self._layout = QGridLayout()
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.addWidget(self._area)
        self.setLayout(self._layout)

        self._controls.goto_index(0)
        self.change_index(0)

    def initUI(self):
        lay = QVBoxLayout()
        self.lay = lay

        lay.setContentsMargins(0, 0, 0, 0)

        self._grid = Grid()
        lay.addWidget(self._grid)
        self.setup_displays_grid()

        contLay = QGridLayout()

        if self._controller.get_layouts() is not None and len(self._controller.get_layouts()) > 0:
            self._layout_nameDropdown = QComboBox()
            contLay.addWidget(self._layout_nameDropdown, 1, 0, 1, 1)

            cur_layout = self._controller.layout.name
            cur_layout_idx = 0
            for idx, layout in enumerate(self._controller.get_layouts()):
                self._layout_nameDropdown.addItem(layout)
                if layout == cur_layout:
                    cur_layout_idx = idx

            self._layout_nameDropdown.setCurrentIndex(cur_layout_idx)
            self._layout_nameDropdown.currentIndexChanged.connect(self.currentLayoutNameChanged)

        self._slider = IntSlider((0, self._controller.num_items-1))
        contLay.addWidget(self._slider, 1, 1, 1, 1)

        self._sampleName = QLabel()
        contLay.addWidget(self._sampleName, 0, 0, 1, 1)

        self._prevButton = QPushButton("Prev")
        self._prevButton.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self._prevButton.setFixedHeight(50)
        contLay.addWidget(self._prevButton, 1, 2, 1, 1)

        self._nextButton = QPushButton("Next")
        self._nextButton.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self._nextButton.setFixedHeight(50)
        contLay.addWidget(self._nextButton, 1, 3, 1, 1)

        self._playButton = QPushButton("Play")
        self._playButton.setCheckable(True)
        self._playButton.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self._playButton.setFixedHeight(50)
        contLay.addWidget(self._playButton, 1, 4, 1, 1)

        widget = QWidget()
        widget.setLayout(contLay)
        lay.addWidget(widget)

        self.setLayout(lay)

        self.gotoIndex(0)

        self._slider.valueChanged.connect(self.gotoIndex)
        self._prevButton.clicked.connect(self.previous)
        self._nextButton.clicked.connect(self.next)
        self._playButton.clicked.connect(self.play)

    def currentLayoutNameChanged(self):
        layout = self._layout_nameDropdown.currentText()
        self._controller.set_layout(layout)
        self._grid.clearWidget()

        new_grid = Grid()
        self.lay.replaceWidget(self._grid, new_grid)
        self._grid = new_grid
        self._grid.setPlaceholders()
        self.setup_displays_grid()
        self.gotoIndex(self._index, True)

        # There is probably some caching issue with the widgets sizes.
        # As soon as main window is unmaximized and then maximized. The sizes
        # of the inner widgets are perfectly proportionate.
        self.showNormal()
        self.update()
        self.showMaximized()

    def setup_displays_grid(self):
        """
        Adds all the displays in the grid.
        """
        self.last_positions = []
        for (x, y), display in self._controller.displays.items():
            self.last_positions.append((x,y))
            self._grid.setWidget(x, y, display)
        self._grid.add_hidden_buttons_rows()
        self._grid.add_hidden_buttons_cols()

    def gotoIndex(self, index, ignore_same=False):

        if self._index == index and not ignore_same:
            return

        self._index = index
        grid_data, info_dict = self._controller.get_item(self._index, get_info=True)

        for (x, y), display_data in grid_data.items():
            widget = self._grid.widget(x, y)
            if isinstance(widget, Vis3dDisplay):
                # Vis3dDisplay widget should be able preserve viewpoint
                # between frame changes.
                camera = widget.renderer.GetActiveCamera()
                widget.setTo(**display_data)
                widget.renderer.SetActiveCamera(camera)
            else:
                widget.setTo(**display_data)

        self._slider.changeValue(index)
        self._sampleName.setText(info_dict['_name'])

        print()
        print("Current sample info:")
        pprint(info_dict)

    def next(self):
        if self._index < self._controller.num_items-1:
            self.gotoIndex(self._index + 1)

    def play(self):
        if self._index < self._controller.num_items-1:
            self.gotoIndex(self._index + 1)

        if self._playButton.isChecked():
            QTimer.singleShot(10, self.play)

    def previous(self):
        if self._index > 0:
            self.gotoIndex(self._index - 1)


class GridMapper:
    def __init__(self):
        self._maps = {}
        self._cfg = {}

    def set(self, pos, display, func=None):
        self._maps[pos] = func
        self._cfg[pos] = display

    def map(self, numItems):
        items = []

        for i in range(0, numItems):
            item = {}

            for pos, func in self._maps.items():
                if func is not None:
                    item[pos] = func(i)

            items.append(item)

        return self._cfg, items
