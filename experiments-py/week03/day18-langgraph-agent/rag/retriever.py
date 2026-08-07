from .vector_store import search_vector_db

# # retrieve 检索
# def retrieve_context(question: str) -> str:
#     """检索相关上下文"""
#     related_chunks = search_vector_db(question)
#     context = "\n\n".join(related_chunks)
#     return context

class Retriever:
    def search(self, query):
        """检索相关上下文"""
        related_chunks = search_vector_db(query)
        context = "\n\n".join(related_chunks)
        return context