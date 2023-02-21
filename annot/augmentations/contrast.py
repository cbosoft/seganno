import numpy as np

from PySide6.QtWidgets import QSlider
from PySide6.QtCore import Qt

from .base import Augmentation


class ContrastAdjust(Augmentation):

    def __init__(self):
        super().__init__('Contrast')
        self.step = 0.05
        self.w = None

    def apply_to_image(self, image: np.ndarray):
        v = self.w.value() * self.step
        image *= v

    def widget(self, update_f):
        self.w = QSlider(Qt.Orientation.Horizontal)
        self.w.setMinimum(int(0.1 / self.step))
        self.w.setValue(int(1.0 / self.step))
        self.w.setMaximum(int(5.0 / self.step))
        self.w.valueChanged.connect(update_f)
        return self.w

    def reset(self):
        self.w.setValue(int(1.0 / self.step))
