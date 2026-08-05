from tools.base import Tool
from rag.vector_store import search_vector_db


class Knowledge(Tool):
    name = "knowledge_search"

    description = """
查询 Agent 知识库。
输入 query：用户问题。
适用于：技术概念解释、项目架构说明、文档内容查询。
"""

    def run(self, query):
        """
        查询知识库

        Args:
            query:
                用户问题

        Returns:
            相关知识内容
        """
        results = search_vector_db(query)
        if not results:
            return "知识库中没有找到相关内容"

        context = "\n\n".join(
            f"资料{i + 1}:\n{chunk}" for i, chunk in enumerate(results)
        )
        return context
