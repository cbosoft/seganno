from PySide6.QtGui import QPainter, QColor

from ..annotation import Annotation
from .tool_base import Tool


class GrabTool(Tool):

    show_next_point = False
    icon = 'pan_hand'

    def __init__(self):
        self.selected = None
        self.point_index = None

    def draw_cursor(self, x, y, p: QPainter):
        p.setPen(QColor(0, 0, 255, 255))
        p.drawLine(x, y-10, x, y+10)
        p.drawLine(x-10, y, x+10, y)

    @staticmethod
    def get_nearest_point_index(x, y, a):
        i, _ = sorted(list(enumerate(a.points)), key=lambda ip: ((ip[1][0] - x)**2.0 + (ip[1][1] - y)**2.0)**0.5)[0]
        return i

    def add(self, x, y, a: Annotation):
        self.selected = a
        self.point_index = self.get_nearest_point_index(x, y, a)

    def add_move(self, x, y, a: Annotation):
        if self.selected is not None:
            self.selected.points[self.point_index] = (x, y)

    def remove(self, x, y, a: Annotation):
        pass

    def remove_move(self, x, y, a: Annotation):
        pass

    def draw_widgets(self, mouse_pos, a: Annotation, p: QPainter, _):
        if mouse_pos is None:
            return

        if self.selected is None:
            x, y = a.points[self.get_nearest_point_index(*mouse_pos, a)]
        else:
            x, y = self.selected.points[self.point_index]

        p.drawEllipse(x-5, y-5, 10, 10)

    def mouse_release(self, is_left: bool):
        if is_left:
            self.selected = self.point_index = None
