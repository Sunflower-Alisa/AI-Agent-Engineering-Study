from chromadb.utils.embedding_functions import DefaultEmbeddingFunction

import chromadb
from pathlib import Path

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
