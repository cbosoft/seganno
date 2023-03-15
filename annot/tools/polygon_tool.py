from PySide6.QtGui import QPainter, QColor

from ..annotation import Annotation
from .tool_base import Tool


class PolygonTool(Tool):

    show_next_point = True
    icon = 'polygon'

    def draw_cursor(self, x, y, p: QPainter):
        p.setPen(QColor(0, 0, 255, 255))
        p.drawLine(x, y-10, x, y+10)
        p.drawLine(x-10, y, x+10, y)

    def add(self, x, y, a: Annotation):
        a.points.append((x, y))

    def add_move(self, x, y, a: Annotation):
        pass

    def remove(self, x, y, a: Annotation):
        a.points.pop()

    def remove_move(self, x, y, a: Annotation):
        pass
