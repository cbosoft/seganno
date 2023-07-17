from PySide6.QtGui import QPainter

from ..annotation import Annotation


class Tool:

    show_next_point = False
    icon = None

    def reset(self):
        pass

    def draw_cursor(self, x, y, p: QPainter):
        raise NotImplementedError

    def add(self, x, y, a: Annotation):
        raise NotImplementedError

    def add_move(self, x, y, a: Annotation):
        raise NotImplementedError

    def remove(self, x, y, a: Annotation):
        raise NotImplementedError

    def remove_move(self, x, y, a: Annotation):
        raise NotImplementedError

    def mouse_release(self, is_left: bool):
        pass

    def draw_widgets(self, mouse_pos, a: Annotation, p: QPainter):
        pass
