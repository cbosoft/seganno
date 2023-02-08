from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QPushButton,
    QGroupBox,
)

from .canvas import Canvas
from .tool_box import ToolBox
from .palette import ClassPalette
from .particles import ParticleBrowser
from .dataset_browser import DatasetBrowser


class MainWindow(QMainWindow):

    SIDE_PANEL_SIZE = 200

    def __init__(self):
        super().__init__()

        self.setMouseTracking(True)
        self.canvas = Canvas(self)
        self.toolbox = ToolBox(self)
        self.class_palette = ClassPalette(self)
        self.particle_browser = ParticleBrowser(self)
        self.dataset_browser = DatasetBrowser(self)

        cw = QWidget()
        self.setCentralWidget(cw)
        cw.layout = QHBoxLayout(cw)

        left = QWidget()
        left.setMaximumWidth(self.SIDE_PANEL_SIZE)
        left.setMinimumWidth(self.SIDE_PANEL_SIZE)
        left.layout = QVBoxLayout(left)
        left.layout.addWidget(self.toolbox)
        left.layout.addWidget(self.class_palette)

        # TODO: ZOOM
        # zoom_group = QGroupBox('Zoom')
        # left.layout.addWidget(zoom_group)
        # zoom_group.layout = QHBoxLayout(zoom_group)
        # btn_zoom_in = QPushButton('+')
        # btn_zoom_in.clicked.connect(self.canvas.zoom_in)
        # btn_zoom_out = QPushButton('-')
        # btn_zoom_out.clicked.connect(self.canvas.zoom_out)
        # zoom_group.layout.addWidget(btn_zoom_in)
        # zoom_group.layout.addWidget(btn_zoom_out)

        centre = QWidget()
        centre.layout = QVBoxLayout(centre)
        canvas_container = QWidget()
        centre.layout.addWidget(canvas_container)
        self.canvas.setParent(canvas_container)

        right = QWidget()
        right.setMaximumWidth(self.SIDE_PANEL_SIZE*2)
        right.setMinimumWidth(self.SIDE_PANEL_SIZE*2)
        right.layout = QVBoxLayout(right)
        right.layout.addWidget(self.particle_browser)
        right.layout.addWidget(self.dataset_browser)

        cw.layout.addWidget(left)
        cw.layout.addWidget(centre)
        cw.layout.addWidget(right)

        self.resize(1280, 720)
        self.setMouseTracking(True)

    def set_image(self, image_fn: str, image_id: int, annot_storage: list):
        self.particle_browser.set_annotations(annot_storage, image_id)
        self.canvas.set_image(image_fn)
