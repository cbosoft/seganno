from .base import Augmentation
from .composed import ComposedAugmentations
from .brightness import BrightnessAdjust
from .contrast import ContrastAdjust
from .filter_smoothing_3x3 import Smooth
from .filter_edgedet_3x3 import EdgeDet
from .torch_augs import ResNetFeatDet


def get_augs() -> ComposedAugmentations:
    augs = [
        BrightnessAdjust(),
        ContrastAdjust(),
        Smooth(),
        EdgeDet(),
    ]

    if ResNetFeatDet is not None:
        augs.append(ResNetFeatDet())

    return ComposedAugmentations(augs)
