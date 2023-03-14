from PySide6.QtWidgets import QGroupBox, QVBoxLayout, QRadioButton, QPushButton

from .tools import TOOLS, Tool


class ToolBox(QGroupBox):

    def __init__(self, app):
        super().__init__('Tool Box')
        self.app = app
        self.selected_tool = None

        self.layout = QVBoxLayout(self)

        for tool_name, tool in TOOLS.items():
            tool.name = tool_name
            chk = QRadioButton(tool_name)
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
