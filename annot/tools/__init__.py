from .tool_base import Tool
from .polygon_tool import PolygonTool
from .brush import BrushTool
from .circle_tool import CircleTool
from .grab import GrabTool

TOOLS = {
    'Polygon Tool': PolygonTool(),
    'Sweeping Brush Tool': BrushTool(),
    'Circle Tool': CircleTool(),
    'Grab Tool': GrabTool(),
}
