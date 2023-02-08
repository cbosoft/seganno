from typing import Optional, List

import numpy as np
import scipy.ndimage

from PySide6.QtWidgets import QGroupBox, QFormLayout, QSlider, QCheckBox
from PySide6.QtCore import Qt


class Augmentation:

    def __call__(self, image: np.ndarray):
        self.apply_to_image(image)
    
    def apply_to_image(self, image: np.ndarray):
        raise NotImplementedError
    
    def update(self, v):
        pass


class ComposedAugmentations(Augmentation):

    def __init__(self, augs: List[Augmentation]):
        self.augs = augs

    def apply_to_image(self, image: np.ndarray):
        for aug in self.augs:
            aug.apply_to_image(image)

class ContrastAdjust(Augmentation):

    def __init__(self):
        self.v = 1.0
    
    def apply_to_image(self, image: np.ndarray):
        image *= self.v
    
    def update(self, v: int):
        self.v = v*0.1

class BrightnessAdjust(Augmentation):

    def __init__(self):
        self.v = 0.0
    
    def apply_to_image(self, image: np.ndarray):
        image += self.v
    
    def update(self, v: int):
        self.v = v*0.1


class Filter2D_Aug(Augmentation):

    def __init__(self, kernel):
        self.kernel = kernel
        self.active = False
    
    def apply_to_image(self, image: np.ndarray):
        if self.active:
            out = scipy.ndimage.convolve(image, self.kernel)
            image[:] = out
    
    def update(self, active: bool):
        self.active = active


class Smooth(Filter2D_Aug):

    def __init__(self):
        super().__init__(np.array([
            [1, 1, 1],
            [1, 1, 1],
            [1, 1, 1]
        ])*(1./9.))


class EdgeDet(Filter2D_Aug):

    def __init__(self):
        super().__init__(np.array([
            [-1, -1, -1],
            [-1, 8, -1],
            [-1, -1, -1]
        ]))


class AugmentationToolbox(QGroupBox):

    def __init__(self, app):
        super().__init__('Image Adjustments')
        self.app = app
        self.layout= QFormLayout(self)

        augs = []
        contrast = ContrastAdjust()
        augs.append(contrast)
        contrast_slider = QSlider(Qt.Orientation.Horizontal)
        contrast_slider.setMinimum(10)
        contrast_slider.setMaximum(50)
        self.layout.addRow('Contrast', contrast_slider)
        contrast_slider.valueChanged.connect(
            lambda: self.update_tfm_and_image(
                lambda: contrast.update(contrast_slider.value())))
        
        brightness = BrightnessAdjust()
        augs.append(brightness)
        brightness_slider = QSlider(Qt.Orientation.Horizontal)
        brightness_slider.setMinimum(0)
        brightness_slider.setMaximum(127)
        self.layout.addRow('Brightness', brightness_slider)
        brightness_slider.valueChanged.connect(
            lambda: self.update_tfm_and_image(
                lambda: brightness.update(brightness_slider.value())))
        
        smooth = Smooth()
        augs.append(smooth)
        smooth_chkbox = QCheckBox('active')
        self.layout.addRow('Smoothing', smooth_chkbox)
        smooth_chkbox.clicked.connect(
            lambda: self.update_tfm_and_image(
                lambda: smooth.update(smooth_chkbox.isChecked() )))
        
        edgedet = EdgeDet()
        augs.append(edgedet)
        edgedet_chkbox = QCheckBox('active')
        self.layout.addRow('Edge Detection', edgedet_chkbox)
        edgedet_chkbox.clicked.connect(
            lambda: self.update_tfm_and_image(
                lambda: edgedet.update(edgedet_chkbox.isChecked() )))

        self.augmentations = ComposedAugmentations(augs)

        self.disable_chk = QCheckBox()
        self.disable_chk.clicked.connect(self.app.canvas.set_image_from_array)
        self.layout.addRow('Disable all', self.disable_chk)

    def update_tfm_and_image(self, f):
        f()
        self.app.canvas.set_image_from_array()
    
    def get_transform(self) -> Augmentation:
        if self.disable_chk.isChecked():
            return ComposedAugmentations([])
        else:
            return self.augmentations
