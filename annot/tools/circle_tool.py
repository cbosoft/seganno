from PySide6.QtGui import QPainter, QColor

import numpy as np

from ..annotation import Annotation
from .tool_base import Tool


class CircleTool(Tool):

    show_next_point = False
    icon = 'circle'

    def __init__(self):
        self.start = None
    
    @staticmethod
    def get_points(start, end):
        sx, sy = start
        ex, ey = end
        cx = (sx + ex)*0.5
        cy = (sy + ey)*0.5
        diameter = ((ey - sy)**2.0 + (ex - sx)**2.0)**0.5
        r = diameter*0.5

        points = []
        for theta in np.linspace(0, np.pi*2.0, 51):
            x = cx + r*np.sin(theta)
            y = cy + r*np.cos(theta)
            points.append((float(x), float(y)))
        return points

    def draw_cursor(self, x, y, p: QPainter):
        if self.start is not None:
            sx, sy = self.start
            cx = (sx + x)*0.5
            cy = (sy + y)*0.5
            w = h = _diameter = ((y - sy)**2.0 + (x - sx)**2.0)**0.5
            p.setPen(QColor(0, 127, 0, 255))
            p.drawEllipse(cx-w/2, cy-h/2, w, h)
            p.setPen(QColor(0, 0, 255, 255))
            p.drawLine(sx, sy, x, y)
        else:
            p.setPen(QColor(0, 0, 255, 255))
            p.drawEllipse(x-2, y-2, 4, 4)

    def add(self, x, y, a: Annotation):
        if self.start is None:
            self.start = (x, y)
            a.points = []
        else:
            start = self.start
            self.start = None
            end = (x, y)
            a.points = self.get_points(start, end)
            # TODO!
            # a.set_label(3)  # circle... its probably a sphere

    def add_move(self, x, y, a: Annotation):
        pass

    def remove(self, x, y, a: Annotation):
        if self.end is not None:
            self.end = None
        else:
            self.start = None

    def remove_move(self, x, y, a: Annotation):
        pass
