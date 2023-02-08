from .tool_base import Tool
from .polygon_tool import PolygonTool
from .brush import BrushTool

TOOLS = {
    'Polygon Tool': PolygonTool(),
    'Brush Tool': BrushTool()
}
