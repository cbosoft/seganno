from typing import Tuple

from matplotlib.path import Path
import numpy as np

from .class_labels import CLASS_COLOURS
from .guess_label import guess_class


class Annotation:

    def __init__(self, image_size: Tuple[int, int], points=tuple(), class_label=1):
        self.image_width, self.image_height = self.image_size = image_size
        self.points = list(points)
        self.id_no = None
        self.im_id = None
        self.class_label = class_label

        self.is_editing = False
        self.is_selected = False

    def __contains__(self, pt):
        return Path(self.points).contains_point(pt)

    @property
    def colour(self):
        return CLASS_COLOURS[self.class_label]

    def set_label(self, label: int):
        assert label > 0
        self.class_label = label

    def as_coco_annot(self) -> dict:
        points = np.array(self.points)
        px = points[:, 0]
        py = points[:, 1]
        x1, x2, y1, y2 = min(px), max(px), min(py), max(py)
        w, h = x2 - x1, y2 - y1
        area = w*h
        bbox = x1, y1, w, h
        bbox = tuple([int(v) for v in bbox])
        pjoined = np.zeros(2*len(px))
        pjoined[::2] = px
        pjoined[1::2] = py

        if area < 1:
            raise RuntimeError

        return dict(
            id=self.id_no,
            image_id=self.im_id,
            category_id=self.class_label,
            bbox=bbox,
            segmentation=[[int(v) for v in pjoined]],
            area=float(area),
            iscrowd=0
        )

    @classmethod
    def from_coco(cls, images_by_id, *, id, image_id: int, category_id: int, bbox, segmentation, area, iscrowd, **_) -> "Annotation":
        _ = bbox
        _ = area
        _ = iscrowd
        px = segmentation[0][::2]
        py = segmentation[0][1::2]
        points = [[pxi, pyi] for pxi, pyi in zip(px, py)]
        im = images_by_id[image_id]
        w, h = im.width, im.height
        rv = cls(image_size=(w, h), points=tuple(points), class_label=category_id)
        rv.im_id = image_id
        rv.coco_id = id
        rv.bbox = bbox
        return rv

    def cv_contour(self):
        pts_arr = np.array(self.points, dtype=int)
        return pts_arr[:, np.newaxis, :]

    def stop_editing(self, callback):
        self.is_editing = False

        if self.class_label < 1:
            self.class_label = guess_class(self.cv_contour())
            assert self.class_label > 0
            callback()
