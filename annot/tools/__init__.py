from .tool_base import Tool
from .polygon_tool import PolygonTool
from .brush import BrushTool
from .circle_tool import CircleTool
from .grab import GrabTool
from .bike_pump import BikePumpTool

TOOLS = {
    'Polygon Tool': PolygonTool(),
    'Sweeping Brush Tool': BrushTool(),
    'Circle Tool': CircleTool(),
    'Grab Tool': GrabTool(),
    'Bike Pump': BikePumpTool(),
}
