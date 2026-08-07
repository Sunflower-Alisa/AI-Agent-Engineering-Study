from .registry import register
from .calculator import CalculatorTool
from .search import SearchTool
from .knowledge import KnowledgeSearchTool
from rag.retriever import Retriever


register(CalculatorTool())
register(SearchTool())
register(KnowledgeSearchTool(Retriever()))