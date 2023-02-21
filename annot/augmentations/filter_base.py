import numpy as np
import scipy.ndimage

from PySide6.QtWidgets import QCheckBox

from .base import Augmentation


class Filter2D_Aug(Augmentation):

    def __init__(self, kernel, name):
        super().__init__(name)
        self.kernel = kernel
        self.w = None

    def apply_to_image(self, image: np.ndarray):
        if self.w.isChecked():
            out = scipy.ndimage.convolve(image, self.kernel)
            image[:] = out

    def widget(self, update_f):
        self.w = QCheckBox('active?')
        self.w.setChecked(False)
        self.w.clicked.connect(update_f)
        return self.w

    def reset(self):
        self.w.setChecked(False)
