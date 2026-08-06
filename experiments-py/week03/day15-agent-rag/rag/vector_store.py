from .embedding import collection

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
