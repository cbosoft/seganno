from PySide6.QtGui import QWheelEvent


class WheelState:

    def __init__(self):
        self.zoom_in = self.zoom_out = False
        self.pan_up = self.pan_down = False
        self.pan_left = self.pan_right = False

    def update(self, event: QWheelEvent):
        delta = event.angleDelta().y()
        # if delta > 0:
        #     self.zoom_in = True
        #     self.zoom_out = False
        # elif delta < 0:
        #     self.zoom_in = False
        #     self.zoom_out = True
