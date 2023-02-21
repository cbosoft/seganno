from typing import List

import numpy as np

from .base import Augmentation


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
