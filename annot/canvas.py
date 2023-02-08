from enum import Enum

from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPaintEvent, QPainter, QMouseEvent, QColor, QImage, QBrush, QPainterPath, QPixmap
from PySide6.QtCore import Qt

from .annotation import Annotation


class InputState(Enum):
    Idle = 0
    DraggingLeft = 1
    DraggingRight = 2


class Canvas(QWidget):

    def __init__(self, app):
        super().__init__()
        self.app = app
        self.mouse_pos = (0, 0)
        self.mouse_screen_pos = (0, 0)
        self.pan_mouse_start_pos = (0, 0)
        self.pan_start_pos = (0, 0)
        self.image = None
        self.image_size = (1000, 1000)

        self.setMouseTracking(True)
        self.resize(1000, 1000)
        self.setCursor(Qt.CursorShape.BlankCursor)

        self.input_state = InputState.Idle

    def mouseMoveEvent(self, event: QMouseEvent):
        self.mouse_pos = event.pos().x(), event.pos().y()
        self.mouse_screen_pos = event.screenPos().x(), event.screenPos().y()

        if self.input_state == InputState.Idle:
            pass
        elif (self.input_state == InputState.DraggingLeft) or (self.input_state == InputState.DraggingRight):
            if Qt.KeyboardModifier.ShiftModifier in event.modifiers():
                self.pan()
            else:
                self.add_or_remove_move(self.input_state == InputState.DraggingLeft)
        else:
            raise ValueError(f'Unhandled input state {self.input_state}')

        event.accept()
        self.repaint()

    def mousePressEvent(self, event: QMouseEvent):
        self.input_state = InputState.DraggingLeft if event.button() == Qt.MouseButton.LeftButton else InputState.DraggingRight
        if Qt.KeyboardModifier.ShiftModifier in event.modifiers():
            self.pan_mouse_start_pos = self.mouse_screen_pos
            self.pan_start_pos = self.pos().x(), self.pos().y()
        else:
            self.add_or_remove(event.button() == Qt.MouseButton.LeftButton)

    def mouseDoubleClickEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            if Qt.KeyboardModifier.ShiftModifier in event.modifiers():
                pass
            else:
                self.end_path()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        self.input_state = InputState.Idle
        self.pan_start_pos = self.pan_mouse_start_pos = None

    def end_path(self):
        self.app.particle_browser.finish_with_current()

    def add_or_remove(self, should_add: bool):
        tool = self.get_current_tool()
        annotation = self.get_current_annotation(should_add)
        if should_add:
            tool.add(*self.mouse_pos, annotation)
        elif annotation:
            tool.remove(*self.mouse_pos, annotation)
        self.repaint()

    def add_or_remove_move(self, should_add: bool):
        tool = self.get_current_tool()
        annotation = self.get_current_annotation(should_add)
        print(should_add, tool, annotation)
        if should_add:
            tool.add_move(*self.mouse_pos, annotation)
        elif annotation:
            tool.remove_move(*self.mouse_pos, annotation)
        self.repaint()

    def get_current_tool(self):
        return self.app.toolbox.current_tool()

    def get_current_annotation(self, create_if_not_exists: bool):
        annot = self.app.particle_browser.get_current_annotation(*self.mouse_pos)
        if annot is None and create_if_not_exists:
            annot = Annotation(self.image_size, class_label=self.app.class_palette.selected_class)
            self.app.particle_browser.add_annotation(annot, is_current=True)
        return annot

    def pan(self):
        if self.pan_mouse_start_pos is None:
            return
        mx, my = self.mouse_screen_pos
        sx, sy = self.pan_mouse_start_pos
        ox, oy = self.pan_start_pos
        self.move(ox + (mx - sx), oy + (my - sy))

    def zoom_in(self):
        pass

    def zoom_out(self):
        pass

    def set_image(self, image_fn: str):
        self.image = QImage(image_fn)
        self.image_size = self.image.width(), self.image.height()
        self.resize(self.image.size())
        self.repaint()

    def paintEvent(self, event: QPaintEvent):
        # TODO: scale for zooming
        # s = 2.0
        # if self.image is not None:
        #     im_w, im_h = self.image.size().width(), self.image.size().height()
        #     self.resize(int(im_w*s), int(im_h*s))
        p = QPainter()
        p.begin(self)
        p.setRenderHint(QPainter.Antialiasing)
        # p.scale(s, s)
        if self.image:
            p.drawImage(0, 0, self.image)

        # Border
        p.setPen(QColor(0, 0, 0, 255))
        p.drawRect(1, 1, self.width()-1, self.height()-1)

        # Annotations
        for annot in self.app.particle_browser.annotations:
            self.draw_annotation(annot, p, annot == self.app.particle_browser.current)

        # cursor
        self.app.toolbox.current_tool().draw_cursor(*self.mouse_pos, p)
        p.end()

    @staticmethod
    def draw_polyg(p: QPainter, polyg, filled: bool, colour, fill_opacity):
        assert polyg
        path = QPainterPath()
        path.moveTo(*polyg[0])
        for pt in polyg[1:]:
            path.lineTo(*pt)
        path.lineTo(*polyg[0])
        if filled:
            c = QColor(colour)
            c.setAlpha(fill_opacity)
            p.fillPath(path, c)
        p.drawPath(path)

    def draw_annotation(self, annot: Annotation, p: QPainter, is_editing: bool):
        if annot.points:
            if is_editing and self.get_current_tool().show_next_point:
                polyg = [*annot.points, self.mouse_pos]
            else:
                polyg = annot.points

            self.draw_polyg(p, polyg, True, annot.colour, 127)
