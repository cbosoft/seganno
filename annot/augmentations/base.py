import numpy as np


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
