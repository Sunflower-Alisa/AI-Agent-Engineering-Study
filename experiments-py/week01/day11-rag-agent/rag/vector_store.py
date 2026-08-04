from pathlib import Path

import chromadb
from chromadb.utils.embedding_functions import DefaultEmbeddingFunction

# 选用 chroma 内置的轻量 ONNX 嵌入模型（all-MiniLM-L6-v2），零额外依赖
embedding_fn = DefaultEmbeddingFunction()

# 持久化向量数据库，数据保存在脚本目录下 ./chroma_db
BASE_DIR = Path(__file__).resolve().parent.parent
client = chromadb.PersistentClient(path=str(BASE_DIR / "chroma_db"))

# 创建/获取集合
collection = client.get_or_create_collection(
    name="agent_knowledge",
    embedding_function=embedding_fn,
)


def add_chunks_to_vector_db(chunks: list[str]):
    """将文本块写入向量数据库；重复构建用 upsert，避免 ID 冲突"""
    ids = [f"chunk_{idx}" for idx in range(len(chunks))]
    collection.upsert(documents=chunks, ids=ids)


def clear_collection():
    """清空集合，用于重建知识库时避免历史数据残留"""
    ids = collection.get()["ids"]
    if ids:
        collection.delete(ids=ids)


def search_vector_db(query: str, top_k: int = 2) -> list[str]:
    """根据问题检索相似度最高的文本片段"""
    result = collection.query(
        query_texts=[query],
        n_results=top_k,
    )
    return result["documents"][0]
