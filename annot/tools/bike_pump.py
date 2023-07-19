import numpy as np

from PySide6.QtGui import QPainter, QColor

from ..annotation import Annotation
from .tool_base import Tool


class BikePumpTool(Tool):

    show_next_point = False
    icon = 'expand'

    def draw_cursor(self, x, y, p: QPainter):
        p.drawRect(x-2, y-2, 4, 4)

    def add(self, x, y, a: Annotation):
        _ = x, y
        self.pump(a, True)

    def add_move(self, x, y, a: Annotation):
        _ = x, y
        self.pump(a, True)

    def remove(self, x, y, a: Annotation):
        _ = x, y
        self.pump(a, False)

    def remove_move(self, x, y, a: Annotation):
        _ = x, y
        self.pump(a, False)

    @staticmethod
    def pump(a: Annotation, should_inflate: bool):
        if len(a.points) < 3:
            return
        x = [p[0] for p in a.points]
        y = [p[1] for p in a.points]
        cx, cy = centroid = np.array([sum(x)/len(x), sum(y)/len(y)])
        delta = 1 if should_inflate else -1
        for i, (px, py) in enumerate(a.points):
            dir = np.array([(px - cx), (py - cy)])
            dir /= np.sqrt(np.dot(dir, dir))
            a.points[i] = float(px + dir[0]*delta), float(py + dir[1]*delta)

    def draw_widgets(self, mouse_pos, a: Annotation, p: QPainter, _):
        x = [p[0] for p in a.points]
        y = [p[1] for p in a.points]
        cx, cy = centroid = np.array([sum(x)/len(x), sum(y)/len(y)])
        # p.setBrush(QColor('black'))
        # p.drawEllipse(cx-3, cy-3, 6, 6)
        # p.setBrush(None)
        for (px, py) in a.points:
            pen = p.pen()
            style = pen.style()
            pen.setStyle(style.DashLine)
            p.setPen(pen)
            p.drawLine(cx, cy, px, py)

