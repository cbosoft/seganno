from PySide6.QtWidgets import QGroupBox, QVBoxLayout, QRadioButton, QPushButton
from PySide6.QtGui import QPaintEvent, QPainter, QImage
from PySide6.QtCore import Qt

from .tools import TOOLS, Tool
from .resources import ICONS


class IconatedRadioButton(QRadioButton):

    ICON_SIZE = 16

    def __init__(self, label, *, icon: str):
        super().__init__(label)
        self.label = label
        self.icon: QImage = ICONS[icon].scaledToHeight(self.ICON_SIZE, Qt.TransformationMode.SmoothTransformation)
    
    def paintEvent(self, ev: QPaintEvent) -> None:
        w = self.width()
        h = self.height()
        p = QPainter()
        p.begin(self)
        m = (h - self.ICON_SIZE) // 2
        if self.isChecked():
            pen = p.pen()
            pen.setWidth(2)
            p.setPen(pen)
            p.drawRect(0, 0, w, h)
        p.drawImage(m, m, self.icon)
        lbl_rect = p.boundingRect(self.ICON_SIZE, 0, w-self.ICON_SIZE, h, 0, self.label)
        p.drawText(self.ICON_SIZE + m + m, lbl_rect.height(), self.label)
        p.end()


class ToolBox(QGroupBox):

    def __init__(self, app):
        super().__init__('Tool Box')
        self.app = app
        self.selected_tool = None

        self.layout = QVBoxLayout(self)

        for tool_name, tool in TOOLS.items():
            tool.name = tool_name
            chk = IconatedRadioButton(tool_name, icon=tool.icon)
            chk.toggled.connect(lambda v, tool=tool: self.selected_tool_changed(v, tool))
            self.layout.addWidget(chk)
            if self.selected_tool is None:
                chk.setChecked(True)
        
        self.stop_editing_button = QPushButton('Stop editing')
        self.layout.addWidget(self.stop_editing_button)
        self.stop_editing_button.clicked.connect(self.stop_editing)
    
    def stop_editing(self):
        self.app.particle_browser.stop_editing()

    def selected_tool_changed(self, v, tool):
        if v:
            self.selected_tool = tool
            self.app.set_info('tool', tool.name)

    def current_tool(self) -> Tool:
        return self.selected_tool
