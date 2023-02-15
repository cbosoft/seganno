from typing import Optional, List

import numpy as np
import scipy.ndimage

from PySide6.QtWidgets import QGroupBox, QFormLayout, QSlider, QCheckBox, QPushButton
from PySide6.QtCore import Qt


class Augmentation:

    def __init__(self, name: str):
        self.name = name

    def __call__(self, image: np.ndarray):
        self.apply_to_image(image)
    
    def apply_to_image(self, image: np.ndarray):
        raise NotImplementedError

    def reset(self):
        raise NotImplementedError
    
    def widget(self, update_f):
        raise NotImplementedError


class ComposedAugmentations(Augmentation):

    def __init__(self, augs: List[Augmentation]):
        super().__init__('')
        self.augs = augs

    def apply_to_image(self, image: np.ndarray):
        for aug in self.augs:
            aug.apply_to_image(image)
    
    def widget(self, update_f):
        return [(aug.name, aug.widget(update_f)) for aug in self.augs]
    
    def reset(self):
        for aug in self.augs:
            aug.reset()
            

class ContrastAdjust(Augmentation):

    def __init__(self):
        super().__init__('Contrast')
        self.step = 0.05
        self.w = None
    
    def apply_to_image(self, image: np.ndarray):
        v = self.w.value()*self.step
        # a = image[:-40].max()
        # n_img = image/a
        # cadj_nimg = np.power(n_img, v)
        image *= v
    
    def widget(self, update_f):
        self.w = QSlider(Qt.Orientation.Horizontal)
        self.w.setMinimum(int(0.1/self.step))
        self.w.setValue(int(1.0/self.step))
        self.w.setMaximum(int(5.0/self.step))
        self.w.valueChanged.connect(update_f)
        return self.w
    
    def reset(self):
        self.w.setValue(int(1.0/self.step))

class BrightnessAdjust(Augmentation):

    def __init__(self):
        super().__init__('Brightness')
        self.step = 0.05
        self.w = None
    
    def apply_to_image(self, image: np.ndarray):
        image += self.w.value()*self.step
    
    def widget(self, update_f):
        self.w = QSlider(Qt.Orientation.Horizontal)
        self.w.setMinimum(int(-127/self.step))
        self.w.setValue(0)
        self.w.setMaximum(int(127/self.step))
        self.w.valueChanged.connect(update_f)
        return self.w
    
    def reset(self):
        self.w.setValue(0)


class Filter2D_Aug(Augmentation):

    def __init__(self, kernel, name):
        super().__init__(name)
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


class Smooth(Filter2D_Aug):

    def __init__(self):
        super().__init__(np.array([
            [1, 1, 1],
            [1, 1, 1],
            [1, 1, 1]
        ])*(1./9.),
        'Smoothing'
        )


class EdgeDet(Filter2D_Aug):

    def __init__(self):
        super().__init__(np.array([
            [-1, -1, -1],
            [-1, 8, -1],
            [-1, -1, -1]
        ]), 'Edge Detection')


class AugmentationToolbox(QGroupBox):

    def __init__(self, app):
        super().__init__('Image Adjustments')
        self.app = app
        self.layout = QFormLayout(self)

        augs = [
            BrightnessAdjust(),
            ContrastAdjust(),
            Smooth(),
            EdgeDet(),
        ]

        self.augmentations = ComposedAugmentations(augs)
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
