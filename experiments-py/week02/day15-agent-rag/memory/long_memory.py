import logging
import hashlib
import struct
from typing import List

import chromadb
from chromadb.config import Settings

logging.getLogger("chromadb").setLevel(logging.WARNING)
logging.getLogger("chromadb.telemetry").setLevel(logging.CRITICAL)


def _compute_embedding(text: str) -> List[float]:
    """基于 MD5 哈希的确定性伪随机向量，无需下载模型"""
    h = hashlib.md5(text.encode("utf-8"))
    digest = h.digest()
    vec = [struct.unpack("f", digest[i : i + 4])[0] for i in range(0, 16, 4)]
    norm = sum(v * v for v in vec) ** 0.5
    return [v / norm for v in vec] if norm > 0 else vec


class LongMemory:       
    def __init__(self, path="./chroma_data", collection_name="agent_memory"):
        self.client = chromadb.PersistentClient(
            path=path,
            settings=Settings(anonymized_telemetry=False),
        )
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"},
        )

    def save(self, key: str, value: str, metadata: dict = None):
        embedding = _compute_embedding(value)
        self.collection.add(
            embeddings=[embedding],
            documents=[value],
            metadatas=[metadata or {}],
            ids=[key],
        )

    def retrieve(self, key: str):
        result = self.collection.get(ids=[key])
        if result["documents"]:
            return result["documents"][0]
        return None

    def search(self, query: str, n_results: int = 3):
        embedding = _compute_embedding(query)
        results = self.collection.query(
            query_embeddings=[embedding],
            n_results=n_results,
        )
        return results["documents"][0] if results["documents"] else []

    def update(self, key: str, value: str, metadata: dict = None):
        self.collection.update(
            documents=[value],
            metadatas=[metadata or {}],
            ids=[key],
        )

    def delete(self, key: str):
        self.collection.delete(ids=[key])

    def count(self):
        return self.collection.count()