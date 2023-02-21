import numpy as np

from .filter_base import Filter2D_Aug


class Smooth(Filter2D_Aug):

    def __init__(self):
        super().__init__(np.array([
                [1, 1, 1],
                [1, 1, 1],
                [1, 1, 1]
            ])*(1./9.),
            'Smoothing'
        )
