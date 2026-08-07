from .base import Tool

class SearchTool(Tool):
    name = "search"

    description = """
    搜索
"""

    def run(self,query):
        
        return "搜索成功"