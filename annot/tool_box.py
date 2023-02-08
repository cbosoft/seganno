from PySide6.QtWidgets import QGroupBox, QVBoxLayout, QRadioButton

from .tools import TOOLS, Tool


class ToolBox(QGroupBox):

    def __init__(self, app):
        super().__init__('Tool Box')
        self.app = app
        self.selected_tool = None

        self.layout = QVBoxLayout(self)

        for tool_name, tool in TOOLS.items():
            chk = QRadioButton(tool_name)
            chk.toggled.connect(lambda v, tool=tool: self.selected_tool_changed(v, tool))
            self.layout.addWidget(chk)
            if self.selected_tool is None:
                chk.setChecked(True)

    def selected_tool_changed(self, v, tool):
        if v:
            self.selected_tool = tool

    def current_tool(self) -> Tool:
        return self.selected_tool
