import math

from PySide6.QtGui import QPainter, QColor

from ..annotation import Annotation
from .tool_base import Tool


class BrushTool(Tool):

    HALF_BRUSH_SIZE = 20

    def draw_cursor(self, x, y, p: QPainter):
        p.setPen(QColor(0, 255, 0, 255))
        p.drawEllipse(x-self.HALF_BRUSH_SIZE, y-self.HALF_BRUSH_SIZE, self.HALF_BRUSH_SIZE*2, self.HALF_BRUSH_SIZE*2)

    def add(self, x, y, a: Annotation):
        pass

    def add_move(self, x, y, a: Annotation):
        for i, (px, py) in enumerate(a.points):
            u = (px - x), (py - y)
            mag = math.sqrt(u[0]*u[0] + u[1]*u[1])
            if mag < self.HALF_BRUSH_SIZE:
                u = u[0]/mag*self.HALF_BRUSH_SIZE, u[1]/mag*self.HALF_BRUSH_SIZE
                a.points[i] = x+u[0], y+u[1]

    def remove(self, x, y, a: Annotation):
        pass

    def remove_move(self, x, y, a: Annotation):
        pass
