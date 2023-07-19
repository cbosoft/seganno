from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QPushButton,
    QGroupBox,
    QSplitter,
    QLabel,
    QSizePolicy,
    QStatusBar,
)
from PySide6.QtCore import Qt

from .canvas import Canvas
from .tool_box import ToolBox
from .palette import ClassPalette
from .particles import ParticleBrowser
from .dataset_browser import DatasetBrowser
from .image_aug import AugmentationToolbox
from .resources import ICONS


class MainWindow(QMainWindow):

    SIDE_PANEL_SIZE = 150

    def __init__(self):
        super().__init__()
        self.info_parts = {}

        self.setMouseTracking(True)
        self.canvas = Canvas(self)
        self.toolbox = ToolBox(self)
        self.class_palette = ClassPalette(self)
        self.particle_browser = ParticleBrowser(self)
        self.dataset_browser = DatasetBrowser(self)
        self.aug_toolbox = AugmentationToolbox(self)
        self.setStatusBar(QStatusBar())

        cw = QSplitter(Qt.Orientation.Horizontal)  # QWidget()
        self.setCentralWidget(cw)
        # cw.layout = QHBoxLayout(cw)

        left = QWidget()
        left.setMaximumWidth(self.SIDE_PANEL_SIZE*2)
        left.setMinimumWidth(self.SIDE_PANEL_SIZE)
        left.layout = QVBoxLayout(left)
        left.layout.addWidget(self.toolbox)
        left.layout.addWidget(self.class_palette)
        left.layout.addWidget(self.aug_toolbox)

        zoom_group = QGroupBox('Zoom')
        left.layout.addWidget(zoom_group)
        zoom_group.layout = QHBoxLayout(zoom_group)
        btn_zoom_in = QPushButton()
        btn_zoom_in.setIcon(QPixmap(ICONS['zoom_in']))
        btn_zoom_in.clicked.connect(self.canvas.zoom_in)
        btn_zoom_out = QPushButton()
        btn_zoom_out.setIcon(QPixmap(ICONS['zoom_out']))
        btn_zoom_out.clicked.connect(self.canvas.zoom_out)
        btn_reset = QPushButton('Reset')
        btn_reset.setIcon(QPixmap(ICONS['reset']))
        btn_reset.clicked.connect(self.canvas.reset_position)
        zoom_group.layout.addWidget(btn_zoom_in)
        zoom_group.layout.addWidget(btn_zoom_out)
        zoom_group.layout.addWidget(btn_reset)

        centre = QWidget()
        centre.layout = QVBoxLayout(centre)
        canvas_container = QWidget()
        canvas_container.setStyleSheet('background-color: white;')
        centre.layout.addWidget(canvas_container)

        self.canvas.setParent(canvas_container)

        right = QWidget()
        right.setMaximumWidth(self.SIDE_PANEL_SIZE*2)
        right.setMinimumWidth(self.SIDE_PANEL_SIZE)
        right.layout = QVBoxLayout(right)
        right.layout.addWidget(self.particle_browser)
        right.layout.addWidget(self.dataset_browser)

        # cw.layout.addWidget(left)
        # cw.layout.addWidget(centre)
        # cw.layout.addWidget(right)
        cw.addWidget(left)
        cw.addWidget(centre)
        cw.addWidget(right)

        self.resize(1280, 720)
        self.setMouseTracking(True)
    
    def set_info(self, k: str, v: str):
        self.info_parts[k] = v
        self.refresh_info_label()
    
    def refresh_info_label(self):
        info_text = ', '.join([f'{k}: {v}' for k, v in self.info_parts.items()])
        self.statusBar().showMessage(info_text)

    def set_image(self, image_fn: str, image_id: int, annot_storage: list):
        self.particle_browser.set_annotations(annot_storage, image_id)
        self.canvas.set_image(image_fn)
