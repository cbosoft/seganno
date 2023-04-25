import cv2
import numpy as np

from .class_labels import CLASSES


def guess_class(contour) -> int:
    perimeter = cv2.arcLength(contour, True)
    area = cv2.contourArea(contour)
    """
    P = pD
    A = pD^2/4
    A = P^2/4p
    """
    circular_equivalent_area = perimeter * perimeter / 4.0 / np.pi
    circularity = area / circular_equivalent_area
    _, (w, h), _ = cv2.minAreaRect(contour)
    w, h = sorted([w, h])
    ar = w / h
    ch = cv2.convexHull(contour)
    ch_area = cv2.contourArea(ch)
    convexity = area / ch_area

    if circularity > 0.85:
        class_label = CLASSES.index('Spherical') + 1
    elif ar < 0.5:
        class_label = CLASSES.index('Elongated') + 1
    elif convexity < 0.9:
        class_label = CLASSES.index('Agglomerated') + 1
    else:
        class_label = CLASSES.index('Regular') + 1

    return class_label
