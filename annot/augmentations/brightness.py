import numpy as np

from PySide6.QtWidgets import QSlider
from PySide6.QtCore import Qt

from .base import Augmentation


class BrightnessAdjust(Augmentation):

    def __init__(self):
        super().__init__('Brightness')
        self.step = 0.05
        self.w = None

    def apply_to_image(self, image: np.ndarray):
        image += self.w.value() * self.step

    def widget(self, update_f):
        self.w = QSlider(Qt.Orientation.Horizontal)
        self.w.setMinimum(int(-127 / self.step))
        self.w.setValue(0)
        self.w.setMaximum(int(127 / self.step))
        self.w.valueChanged.connect(update_f)
        return self.w

    def reset(self):
        self.w.setValue(0)
