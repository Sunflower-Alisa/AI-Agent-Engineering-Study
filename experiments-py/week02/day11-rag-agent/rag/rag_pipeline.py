from .loader import load_file
from .chunker import split_text_langchain

from .vector_store import add_chunks_to_vector_db, search_vector_db


def build_knowledge_base(file_path: str):
    """构建知识库：加载文档 → 切块 → 向量化入库"""
    text = load_file(file_path)
    chunks = split_text_langchain(text)
    add_chunks_to_vector_db(chunks)
    print(f"知识库构建完成，共存入 {len(chunks)} 个文本块")

# retrieve 检索
def retrieve_context(question: str) -> str:
    """检索相关上下文"""
    related_chunks = search_vector_db(question)
    context = "\n\n".join(related_chunks)
    return context
