from PySide6.QtWidgets import QGroupBox, QVBoxLayout, QRadioButton

from .class_labels import CLASSES, CLASS_COLOURS


class ClassPalette(QGroupBox):

    def __init__(self, app):
        super().__init__('Particle Classes')
        self.app = app
        self.selected_class = None

        self.layout = QVBoxLayout(self)

        for i, class_name in enumerate(CLASSES):
            chk = QRadioButton(class_name)
            chk.toggled.connect(lambda v, i=i: self.selected_class_changed(v, i+1))
            self.layout.addWidget(chk)
            if self.selected_class is None:
                chk.setChecked(True)

    def selected_class_changed(self, is_checked, i):
        if is_checked:
            self.selected_class = i
            self.app.set_info('class', CLASSES[i - 1])
