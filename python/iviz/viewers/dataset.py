#!/usr/bin/env python3

from PyQt5.QtWidgets import QGridLayout, QWidget
from itypes import Dataset, Path, File, TraceLogger, is_list
from ..widgets.containers import IVizArea, DisplayGrid
from .. import Manager
from ..widgets.controls import SequenceControls
from PyQt5.QtWidgets import QScrollArea, QAbstractScrollArea, QFrame
from PyQt5.QtGui import QResizeEvent
from PyQt5.Qt import QApplication


class _OversizeScrollArea(QScrollArea):
    def __init__(self, widget):
        super().__init__()
        self.setWidget(widget)
        self.setWidgetResizable(True)
        self.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        self.setFrameShape(QFrame.NoFrame)

    def viewportEvent(self, event):
        if isinstance(event, QResizeEvent):
            min_width = self.widget().minimumSizeHint().width()
            min_height = self.widget().minimumSizeHint().height()
            sg = QApplication.desktop().screenGeometry()
            s_height = sg.height()
            s_width = sg.width()

            width = min(min_width, int(0.9 * s_width))
            height = min(min_height, int(0.9 * s_height))

            self.setMinimumWidth(width)
            self.setMinimumHeight(height)

        return super().viewportEvent(event)

def load_dataset(location, cols=5):
    if isinstance(location, File):
        dataset = Dataset(location).read()
        return dataset, str(location)

    types = {
        "image":  ["png", "exr", "jpg", "tif"],
        "flow": ["flo"],
        "float": ["blob", "np", "npz"]
    }

    path = Path(str(location))
    if not path.is_dir():
        file = File(location)
        if not file.exists:
            raise Exception(f"don't know how to read dataset \"{location}>\"")

        if file.extension() in ["json", "gridseq"]:
            dataset = Dataset(location).read()
            return dataset, dataset.file()

        for type, exts in types.items():
            if file.extension() in exts:
                dataset = Dataset(single_item=True)
                dataset.viz.new_row().add_cell(type, var=type).sv.set_ref(file)
                return dataset, file

    else:
        file = path.file('data.gridseq')
        if file.exists():
            dataset = Dataset(file).read()
            return dataset, dataset.file()

        file = path.file('data.json')
        if file.exists():
            dataset = Dataset(file).read()
            return dataset, dataset.file()

        row = None
        counter = 0
        total  = 0
        vars = []
        def new_var(name):
            org_name = name
            i = 1
            while name in vars:
                name = f"{org_name}_{i}"
                i += 1
            vars.append(name)
            return name

        dataset = Dataset(single_item=True)
        for file in path.list_files():
            for type, exts in types.items():
                if file.extension() in exts:
                    if row is None:
                        row = dataset.viz.new_row()

                    row.add_cell(type, var=new_var(type)).sv.set_ref(file)
                    counter += 1
                    total += 1
                    if counter == cols:
                        counter = 0
                        row = None

        if total > 0:
            return dataset, path

    raise Exception(f"don't know how to read dataset \"{location}\"")

class DatasetViewer(QWidget):
    def __init__(self, dataset, parent=None, cols=5):
        self.__log = TraceLogger()
        super().__init__(parent)

        if not isinstance(dataset, Dataset):
            if is_list(dataset):
                arg_list = dataset
                dataset = Dataset()
                for entry in arg_list:
                    if entry == ",":
                        dataset.new_merge_row()
                        continue
                    entry_ds, entry_loc = load_dataset(entry, cols=cols)
                    dataset.merge(entry_ds, include_label=True)
                self.setWindowTitle('iviz')
            else:
                dataset, location = load_dataset(dataset, cols=cols)
                self.setWindowTitle('iviz: ' + str(location.abs()))

        self._ds = dataset
        self._index = None
        self._displays = {}
        self.initUI()

    def initUI(self):
        self._manager = Manager()

        self._grid = DisplayGrid()
        for viz in self._ds.viz:
            col, row = viz.index()
            display = viz.create_display(self._manager)
            self._grid.set_widget(
                display,
                col,
                row,
                colspan=viz.colspan(),
                rowspan=viz.rowspan()
            )
            self._displays[display.id()] = display

        self._controls = SequenceControls(self._ds)
        self._controls.index_changed.connect(self.change_index)

        self._grid_scroll = _OversizeScrollArea(self._grid)

        self._area = IVizArea(self._manager)
        self._area.set_main_widget(self._grid_scroll)
        self._area.set_controls(self._controls)

        if len(self._ds.viz.ids()) == 1:
            self._area.set_show_drag_and_drop_areas(False)
            self._area.set_show_viz_controls(False)

        self._layout = QGridLayout()
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.addWidget(self._area)
        self.setLayout(self._layout)

        self._controls.goto_index(0)
        self.change_index(0)

    def change_index(self, index):
        if self._index == index: return
        self.__log.debug(f"goto index {index} (old = {self._index})")

        self._index = index
        item = self._ds.seq.full_item_list()[index]
        group_id = item['group_id']
        item_id = item['item_id']

        for id in self._displays:
            if id in self._ds.viz:
                self._displays[id].set_data(self._ds.viz[id].data(group_id, item_id))
            else:
                self._displays[id].set_data(None)

