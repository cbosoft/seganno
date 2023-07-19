from typing import Tuple

from PySide6.QtGui import QPainter, QColor

import numpy as np
from scipy.optimize import minimize

from annot.annotation import Annotation

from ..annotation import Annotation
from .tool_base import Tool


class CircleTool(Tool):

    show_next_point = False
    icon = 'circle'

    def __init__(self):
        self.points = []

    def reset(self):
        self.points = []
    
    def fit_circle(self, additional_point=None) -> Tuple[float, float, float]:
        points = self.points if additional_point is None else [*self.points, additional_point]
        x, y = np.array(points).T
        max_x, max_y = np.max(x), np.max(y)
        min_x, min_y = np.min(x), np.min(y)
        cx, cy = (max_x + min_x)*0.5, (max_y + min_y)*0.5
        r = np.mean(((x - cx)**2. + (y - cy)**2.)**0.5)
        return cx, cy, r

    def interp_points(self, cx, cy, r, n=50):
        points = []
        for theta in np.linspace(0, np.pi*2.0, n + 1):
            x = cx + r*np.sin(theta)
            y = cy + r*np.cos(theta)
            points.append((float(x), float(y)))
        return points

    def draw_cursor(self, x, y, p: QPainter):
        p.setBrush(QColor(0, 0, 0, 0))
        p.setPen(QColor(0, 0, 255, 255))
        p.drawEllipse(x-2, y-2, 4, 4)
    
    def draw_widgets(self, mouse_pos, _: Annotation, p: QPainter, o: int):
        for px, py in self.points:
            p.drawEllipse(px-2 + o, py-2 + o, 4, 4)
        if self.points and mouse_pos:
            mx, my = mouse_pos
            cx, cy, r = self.fit_circle(additional_point=(mx-o, my-o))
            cx, cy, r = int(cx), int(cy), int(r)
            d = r*2
            p.setPen(QColor(0, 0, 255, 255))
            p.drawEllipse(cx-r+o, cy-r+o, d, d)

    def add(self, x, y, a: Annotation):
        self.points.append((x, y))
        a.points = self.interp_points(*self.fit_circle())

    def add_move(self, x, y, a: Annotation):
        pass

    def remove(self, x, y, a: Annotation):
        if self.points:
            _ = self.points.pop(-1)
            a.points = self.interp_points(*self.fit_circle())

    def remove_move(self, x, y, a: Annotation):
        pass
