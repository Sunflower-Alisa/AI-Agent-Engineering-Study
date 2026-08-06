from .calculator import Calculator
from .search import SearchTool
from .knowledge import Knowledge

TOOLS = {
    "calculator" : Calculator(),
    "search" : SearchTool(),
    "knowledge_search": Knowledge()
}