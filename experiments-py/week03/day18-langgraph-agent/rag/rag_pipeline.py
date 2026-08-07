import os

from rag.chunker import split_text_langchain
from rag.loader import load_file
from rag.vector_store import add_chunks_to_vector_db


def build_knowledge_base(file_path: str) -> int:
    """构建知识库：加载文档 → 切块 → 向量化入库，返回入库文本块数"""
    text = load_file(file_path)
    chunks = split_text_langchain(text)
    add_chunks_to_vector_db(chunks)
    print(f"知识库构建完成，共存入 {len(chunks)} 个文本块")
    return len(chunks)


def build_knowledge_base_from_project() -> None:
    """用项目自带示例文档构建知识库"""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    doc_path = os.path.join(base_dir, "documents", "agent.md")
    build_knowledge_base(doc_path)
