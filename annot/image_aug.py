from PySide6.QtWidgets import QGroupBox, QFormLayout, QCheckBox, QPushButton

from .augmentations import Augmentation, ComposedAugmentations, get_augs


class AugmentationToolbox(QGroupBox):

    def __init__(self, app):
        super().__init__('Image Adjustments')
        self.app = app
        self.layout = QFormLayout(self)

        self.augmentations = get_augs()
        update_f = self.app.canvas.set_image_from_array
        for name, w in self.augmentations.widget(update_f):
            self.layout.addRow(name, w)

        self.disable_chk = QCheckBox()
        self.disable_chk.clicked.connect(update_f)
        self.layout.addRow('Disable all', self.disable_chk)
        btn_reset = QPushButton('Reset')
        btn_reset.clicked.connect(self.augmentations.reset)
        self.layout.addRow(' ', btn_reset)
    
    def get_transform(self) -> Augmentation:
        if self.disable_chk.isChecked():
            return ComposedAugmentations([])
        else:
            return self.augmentations
