from .base import Tool

class SearchTool(Tool):
    name = "search"

    description = """
搜索互联网信息
"""

    def run(self,query):
        return f"搜索结果：{query}"