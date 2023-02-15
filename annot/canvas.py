import os
from enum import Enum
from typing import Optional

import numpy as np
import cv2

from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPaintEvent, QPainter, QMouseEvent, QColor, QImage, QBrush, QPainterPath, QPixmap, QPen
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
        self.scale_i = 4
        self.scales = [0.2, 0.4, 0.6, 0.8, 1, 1.2, 1.5, 2.0, 2.5, 3.0, 4.0]
        self.mouse_screen_pos = (0, 0)
        self.pan_mouse_start_pos = (0, 0)
        self.pan_start_pos = (0, 0)

        self.image_array: Optional[np.ndarray] = None
        self.image: Optional[QImage] = None
        self.image_size = (1000, 1000)

        self.setMouseTracking(True)
        self.resize(1000, 1000)
        self.setCursor(Qt.CursorShape.BlankCursor)

        self.input_state = InputState.Idle
    
    @property
    def scale(self):
        self.scale_i = max(min(self.scale_i, len(self.scales)-1), 0)
        return self.scales[self.scale_i]

    def mouseMoveEvent(self, event: QMouseEvent):
        self.mouse_pos = event.pos().x()/self.scale, event.pos().y()/self.scale
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
        self.scale_i += 1
        self.scale_i = max(min(self.scale_i, len(self.scales)-1), 0)
        self.repaint()

    def zoom_out(self):
        self.scale_i -= 1
        self.scale_i = max(min(self.scale_i, len(self.scales)-1), 0)
        self.repaint()
    
    def reset_position(self):
        self.move(0, 0)
        self.scale_i = self.scales.index(1)

    def set_image_from_array(self):
        transform = self.app.aug_toolbox.get_transform()

        f_array = self.image_array.astype(float)
        transform(f_array)
        f_array[f_array > 255.0] = 255.0
        f_array[f_array < 0.0] = 0.0
        i_array = f_array.astype(np.uint8)
        
        h, w = i_array.shape
        self.image = QImage(
            i_array,
            w,
            h,
            w,
            QImage.Format.Format_Grayscale8
        )
        self.image_size = self.image.width(), self.image.height()
        self.resize(self.image.size())
        self.repaint()

    def set_image(self, image_fn: str):
        image_fn = image_fn.replace('/', os.sep).replace('\\', os.sep)
        self.image_array = cv2.imread(image_fn, cv2.IMREAD_GRAYSCALE)
        assert self.image_array is not None, f'Failed to read image {image_fn}'
        self.set_image_from_array()

    def paintEvent(self, event: QPaintEvent):
        # TODO: scale for zooming
        if self.image is not None:
            im_w, im_h = self.image.size().width(), self.image.size().height()
            self.resize(int(im_w*self.scale), int(im_h*self.scale))
        
        p = QPainter()
        p.begin(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.scale(self.scale, self.scale)
        if self.image:
            p.drawImage(0, 0, self.image)

        # Annotations
        for annot in self.app.particle_browser.annotations:
            self.draw_annotation(annot, p, annot == self.app.particle_browser.current)

        # cursor
        self.app.toolbox.current_tool().draw_cursor(*self.mouse_pos, p)
        p.end()

    @staticmethod
    def draw_polyg(p: QPainter, polyg, filled: bool, bordered: bool, dashed_border: bool, colour, fill_opacity: int, bright_border: bool):
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
        if bordered:
            pen = QPen()
            if dashed_border:
                pen.setStyle(Qt.PenStyle.DotLine)
            else:
                pen.setStyle(Qt.PenStyle.SolidLine)
            if bright_border:
                pen.setColor(colour)
                pen.setWidth(3)
            else:
                pen.setColor('#000000')
                pen.setWidth(1)
            p.setPen(pen)
            p.drawPath(path)

    def draw_annotation(self, annot: Annotation, p: QPainter, is_editing: bool):
        if annot.points:
            if is_editing and self.get_current_tool().show_next_point:
                polyg = [*annot.points, self.mouse_pos]
            else:
                polyg = annot.points

            self.draw_polyg(
                p, polyg,
                filled=True,
                bright_border=annot.is_selected and not annot.is_editing,
                bordered=annot.is_selected or annot.is_editing,
                dashed_border=not annot.is_editing, 
                colour=annot.colour,
                fill_opacity=60)
