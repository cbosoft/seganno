from PySide6.QtWidgets import QGroupBox, QVBoxLayout, QRadioButton
from PySide6.QtGui import QPainter, QPaintEvent

from .class_labels import CLASSES, CLASS_COLOURS


class ColourBlobRadioButton(QRadioButton):

    ICON_SIZE = 16

    def __init__(self, label, *, colour: str):
        super().__init__(label)
        self.label = label
        self.colour = colour
    
    def paintEvent(self, ev: QPaintEvent) -> None:
        w = self.width()
        h = self.height()
        p = QPainter()
        p.begin(self)
        m = (h - self.ICON_SIZE) // 2
        p.fillRect(m, m, self.ICON_SIZE-m-m, h-m-m, self.colour)
        if self.isChecked():
            pen = p.pen()
            pen.setWidth(2)
            p.setPen(pen)
            p.drawRect(0, 0, w, h)
        lbl_rect = p.boundingRect(self.ICON_SIZE, 0, w-self.ICON_SIZE, h, 0, self.label)
        p.drawText(self.ICON_SIZE + m + m, lbl_rect.height(), self.label)
        p.end()


class ClassPalette(QGroupBox):

    def __init__(self, app):
        super().__init__('Particle Classes')
        self.app = app
        self.selected_class = None

        self.layout = QVBoxLayout(self)

        for i, class_name in enumerate(CLASSES):
            chk = ColourBlobRadioButton(class_name, colour=CLASS_COLOURS[i+1])
            chk.toggled.connect(lambda v, i=i: self.selected_class_changed(v, i+1))
            self.layout.addWidget(chk)
            if self.selected_class is None:
                chk.setChecked(True)

        chk = ColourBlobRadioButton('GUESS!', colour='#FF00FF')
        chk.toggled.connect(lambda v: self.selected_class_changed(v, -1))
        self.layout.addWidget(chk)
        if self.selected_class is None:
            chk.setChecked(True)

    def selected_class_changed(self, is_checked, i):
        if is_checked:
            self.selected_class = i
            if i > 0:
                self.app.set_info('class', CLASSES[i - 1])
            else:
                self.app.set_info('class', 'unkown class')
