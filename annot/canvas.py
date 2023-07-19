import os
from enum import Enum
from typing import Optional

import numpy as np
import cv2

from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPaintEvent, QPainter, QMouseEvent, QWheelEvent, QColor, QImage, QPainterPath, QPen
from PySide6.QtCore import Qt

from .annotation import Annotation
from .wheel_state import WheelState


class InputState(Enum):
    Idle = 0
    DraggingLeft = 1
    DraggingRight = 2


class Canvas(QWidget):

    OFFSET = 500

    def __init__(self, app):
        super().__init__()
        self.app = app
        self.mouse_pos = self.mouse_widget_pos = None
        self.scale_i = 4
        self.scales = [0.2, 0.4, 0.6, 0.8, 1, 1.2, 1.5, 2.0, 2.5, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]
        self.mouse_screen_pos = (0, 0)
        self.pan_mouse_start_pos = (0, 0)
        self.pan_start_pos = None

        self.image_array: Optional[np.ndarray] = None
        self.image: Optional[QImage] = None
        self.image_size = (1000, 1000)

        self.setMouseTracking(True)
        self.resize(1000 + 2*self.OFFSET, 1000 + 2*self.OFFSET)
        self.reset_position()
        self.setCursor(Qt.CursorShape.BlankCursor)
        self.wheel_state = WheelState()

        self.input_state = InputState.Idle
    
    @property
    def scale(self):
        self.scale_i = max(min(self.scale_i, len(self.scales)-1), 0)
        return self.scales[self.scale_i]
    
    def leaveEvent(self, ev):
        self.mouse_pos = None
        self.repaint()

    def mouseMoveEvent(self, event: QMouseEvent):
        x, y = (event.pos().x() - self.OFFSET)/self.scale, (event.pos().y() - self.OFFSET)/self.scale # pos on image
        x = min(max(0, x), self.image_size[0])
        y = min(max(0, y), self.image_size[1])
        self.mouse_pos = x, y
        self.mouse_widget_pos = event.pos().x()/self.scale, event.pos().y()/self.scale # pos on widget
        self.mouse_screen_pos = event.screenPos().x(), event.screenPos().y()

        if self.input_state == InputState.Idle:
            if not self.app.particle_browser.current:
                self.app.particle_browser.try_select_at_position(self.mouse_pos)
        elif (self.input_state == InputState.DraggingLeft) or (self.input_state == InputState.DraggingRight):
            if self.pan_start_pos is not None:
                self.pan()
            else:
                self.add_or_remove_move(self.input_state == InputState.DraggingLeft)
        else:
            raise ValueError(f'Unhandled input state {self.input_state}')

        event.accept()
        self.repaint()

    def mousePressEvent(self, event: QMouseEvent):
        self.input_state = InputState.DraggingRight if event.button() == Qt.MouseButton.RightButton else InputState.DraggingLeft
        if (Qt.KeyboardModifier.ShiftModifier in event.modifiers()) or (event.button() == Qt.MouseButton.MiddleButton):
            self.pan_mouse_start_pos = self.mouse_screen_pos
            self.pan_start_pos = self.pos().x(), self.pos().y()
        else:
            if self.app.particle_browser.current:
                self.add_or_remove(event.button() == Qt.MouseButton.LeftButton)
            elif self.app.particle_browser.selected and (self.mouse_pos in self.app.particle_browser.selected):
                self.app.particle_browser.edit_selected()
                self.repaint()

    def mouseDoubleClickEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            if Qt.KeyboardModifier.ShiftModifier in event.modifiers():
                pass
            else:
                annot = self.app.particle_browser.current
                if annot:
                    self.end_path()
                else:
                    self.create_new_annot()
                    self.add_or_remove(should_add=True)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        self.input_state = InputState.Idle
        self.pan_start_pos = self.pan_mouse_start_pos = None
        self.get_current_tool().mouse_release(event.button() == Qt.MouseButton.LeftButton)

    def wheelEvent(self, event: QWheelEvent) -> None:
        self.wheel_state.update(event)

        if self.wheel_state.zoom_in:
            self.zoom_in()
        elif self.wheel_state.zoom_out:
            self.zoom_out()
        elif self.wheel_state.pan_up:
            self.manual_pan(0, 5)
        elif self.wheel_state.pan_down:
            self.manual_pan(0, -5)

    def end_path(self):
        self.app.particle_browser.finish_with_current()

    def add_or_remove(self, should_add: bool):
        tool = self.get_current_tool()
        annotation = self.get_current_annotation(False)
        if should_add and annotation:
            tool.add(*self.mouse_pos, annotation)
        elif annotation:
            tool.remove(*self.mouse_pos, annotation)
        self.repaint()

    def add_or_remove_move(self, should_add: bool):
        tool = self.get_current_tool()
        annotation = self.get_current_annotation(False)
        if should_add and annotation:
            tool.add_move(*self.mouse_pos, annotation)
        elif annotation:
            tool.remove_move(*self.mouse_pos, annotation)
        self.repaint()

    def get_current_tool(self):
        return self.app.toolbox.current_tool()
    
    def create_new_annot(self):
        annot = Annotation(self.image_size, class_label=self.app.class_palette.selected_class)
        self.app.particle_browser.add_annotation(annot, is_current=True)
        return annot

    def get_current_annotation(self, create_if_not_exists: bool):
        if self.mouse_pos is None:
            return None
        annot = self.app.particle_browser.get_current_annotation(*self.mouse_pos)
        if annot is None and create_if_not_exists:
            annot = self.create_new_annot()
            self.get_current_tool().reset()
        return annot

    def manual_pan(self, dx, dy):
        mx, my = self.mouse_pos
        self.pan_mouse_start_pos = (mx - dx, my + dy)
        self.pan_start_pos = self.pos().x(), self.pos().y()
        self.pan()

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
        self.move(-self.OFFSET + 4, -self.OFFSET + 4)
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
        self.image_size = w, h = self.image.width(), self.image.height()
        self.resize(w + 2*self.OFFSET, h + 2*self.OFFSET)
        self.repaint()

    def set_image(self, image_fn: str):
        image_fn = image_fn.replace('/', os.sep).replace('\\', os.sep)
        psize = (2000, 2000) if self.image_array is None else self.image_array.shape
        self.image_array = cv2.imread(image_fn, cv2.IMREAD_GRAYSCALE)
        if self.image_array is None:
            print( f'Failed to read image {image_fn}')

            self.image_array = np.zeros(psize, dtype=np.uint8)
        self.set_image_from_array()

    def paintEvent(self, event: QPaintEvent):
        if self.image is not None:
            im_w, im_h = self.image.size().width(), self.image.size().height()
            self.resize(int(im_w*self.scale) + 2*self.OFFSET, int(im_h*self.scale) + 2*self.OFFSET)
        
        p = QPainter()
        p.begin(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.scale(self.scale, self.scale)
        if self.image:
            p.drawImage(self.OFFSET, self.OFFSET, self.image)

        # Annotations
        for annot in self.app.particle_browser.annotations:
            self.draw_annotation(annot, p, annot == self.app.particle_browser.current)

        # cursor
        if self.mouse_pos is not None:
            x, y = self.mouse_pos
            self.app.toolbox.current_tool().draw_cursor(x+self.OFFSET, y+self.OFFSET, p)
            x, y = self.mouse_widget_pos
            pen = QPen()
            pen.setColor('black')
            pen.setWidth(1)
            p.setPen(pen)
            p.setBrush(QColor(0, 0, 0, 255))
            p.drawEllipse(x-1, y-1, 3, 3)
        
        w, h = int(self.width()*self.scale), int(self.height()*self.scale)
        pen = QPen()
        pen.setColor('black')
        pen.setWidth(2)
        p.setPen(pen)
        p.setBrush(QColor(0, 0, 0, 0))
        p.drawRect(2, 2, w-2, h-2)
        p.drawRect(self.OFFSET - 2, self.OFFSET - 2, w+4 - self.OFFSET*2, h+4 - self.OFFSET*2)
        p.end()

    @staticmethod
    def draw_polyg(
            p: QPainter,
            polyg,
            filled: bool,
            bordered: bool,
            dashed_border: bool,
            colour,
            fill_opacity: int,
            bright_border: bool,
            draw_points: bool,
            scale=1.0,
    ):
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

        if draw_points:
            p.setBrush(QColor('black'))
            for (x, y) in polyg:
                w = 6 / scale
                hw = w * 0.5
                p.drawEllipse(x - hw, y - hw, w, w)

    def draw_annotation(self, annot: Annotation, p: QPainter, is_editing: bool):
        if annot.points:
            w, h = self.image_size
            for i, (x, y) in enumerate(annot.points):
                x = min(max(x, 0), w)
                y = min(max(y, 0), h)
                annot.points[i] = (x, y)

            tool = self.get_current_tool()

            if is_editing and tool.show_next_point and self.mouse_pos is not None:
                polyg = [*annot.points, self.mouse_pos]
            else:
                polyg = annot.points

            tool.draw_widgets(self.mouse_pos, annot, p)

            is_generally_annotating = self.get_current_annotation(False)

            polyg = [(x+self.OFFSET, y+self.OFFSET) for x, y in polyg]

            self.draw_polyg(
                p, polyg,
                filled=True,
                bright_border=annot.is_selected and not annot.is_editing,
                bordered=(annot.is_selected and not is_generally_annotating) or annot.is_editing,
                dashed_border=not annot.is_editing, 
                colour=annot.colour,
                fill_opacity=60 if annot.is_editing else (10 if is_generally_annotating else 150),
                draw_points=annot.is_editing,
                scale=self.scale,
            )
