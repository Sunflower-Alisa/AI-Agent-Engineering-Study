from .base import Tool

class KnowledgeSearchTool(Tool):
    name = "knowledge_search"

    description = """
    查询Agent知识库
    用于查询技术文档
"""

    def __init__(self,retriever):
        self.retriever = retriever

    def run(self,args):
        query = args["query"]

        return self.retriever.search(query)