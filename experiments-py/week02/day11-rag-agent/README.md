# Day11 - RAG Agent（RAG 知识库 Agent）

基于检索增强生成（Retrieval-Augmented Generation）的 Agent 示例：把私有文档加载、切块、向量化入库，再根据用户问题检索相关片段，送入 LLM 生成回答。

## 流程

```
Document 原始文档
    ↓
Loader   文档加载器（读取 md/txt）
    ↓
Chunk    文本切分（分段，防止超长）
    ↓
Embedding  向量化（文本 → 数值向量）
    ↓
VectorDB  向量数据库（持久化存储向量）
    ↓
Retriever  检索器（按相似度查找相关片段）
    ↓
Context   检索到的相关片段（作为参考上下文）
    ↓
LLM      大模型（问题 + 上下文一并送入）
    ↓
Answer   最终答案
```

## 结构

```
day11-rag-agent/
├── main.py              # 入口：构建知识库 → 检索 → 拼 Prompt → LLM 生成回答
├── documents/
│   └── agent.md         # 示例知识文档（AI Agent 组成 + RAG 流程说明）
└── rag/
    ├── loader.py        # Loader：读取 md/txt，校验文件存在与扩展名
    ├── chunker.py       # Chunk：LangChain 递归字符切分（chunk_size + chunk_overlap）
    ├── vector_store.py  # VectorDB：chroma 持久化 + 嵌入 + 检索（upsert 防重复、可清空）
    ├── rag_pipeline.py  # 串联：build_knowledge_base / retrieve_context
    └── llm.py           # LLM 封装：chat（复用共享 config.py）
```

## 各模块

| 模块 | 文件 | 作用 |
|---|---|---|
| Loader | `loader.py` | `load_file(path)`：读取文档，校验存在性与 `.md`/`.txt` 扩展名 |
| Chunk | `chunker.py` | `split_text_langchain(text)`：`RecursiveCharacterTextSplitter` 递归按段落/句子切分 |
| Embedding | `vector_store.py` | 用 chroma 内置 `DefaultEmbeddingFunction`（ONNX MiniLM-L6-v2）做文本向量化 |
| VectorDB | `vector_store.py` | `PersistentClient` 持久化；`add_chunks_to_vector_db`（upsert）/ `search_vector_db`（相似度检索）/ `clear_collection` |
| Pipeline | `rag_pipeline.py` | `build_knowledge_base`（加载→切块→入库）、`retrieve_context`（检索→拼上下文） |
| LLM | `llm.py` | `chat(prompt)` 调用大模型生成最终回答 |

## 运行

```bash
cd experiments-py/week01/day11-rag-agent
..\..\.venv\Scripts\python.exe main.py
```

> - 需要 `DEEPSEEK_API_KEY` 环境变量（统一 `experiments-py/config.py`）
> - 首次运行 chroma 会下载 MiniLM 嵌入模型（约 79MB）到 `~/.cache/chroma/onnx_models/`，仅一次

## 检索与回答

`main.py` 流程：
1. `build_knowledge_base(doc_path)`：加载 `documents/agent.md` → 切块 → 向量化入库（数据存于 `chroma_db/`）
2. `retrieve_context(question)`：对用户问题检索相似度最高的片段，拼成参考上下文
3. 用 prompt 模板（只允许基于资料回答、禁止编造）组装，`chat()` 生成最终答案

## 重点注意事项

1. **嵌入模型首次下载**：chroma 首次使用 `DefaultEmbeddingFunction` 要从 S3 下载 79MB 模型。若断网/慢速导致 `ReadTimeout`，可用 `curl -C -` 断点续传下载到 `~/.cache/chroma/onnx_models/all-MiniLM-L6-v2/onnx.tar.gz`，SHA256 匹配后 chroma 直接解锁用
2. **不用 `sentence-transformer` 方案**：`DefaultEmbeddingFunction` 基于 ONNX，无需安装 `torch`/`sentence-transformers` 等大型依赖
3. **数据目录**：`vector_store.py` 用脚本定位（`Path(__file__)`）而非相对 CWD，避免从错误目录建库
4. **重复构建**：`add_chunks_to_vector_db` 用 `upsert` 避免 ID 冲突；重建前可先 `clear_collection()`
5. **Python 3.9 兼容**：类型标注用 `Optional[str]`，不用 `str | None`（PEP 604 需 3.10+）
6. **控制台编码**：Windows 控制台默认为 GBK，print 中避免使用 emoji（如 `✅`），否则报 `UnicodeEncodeError`

## 知识点对应

| RAG 概念 | 对应代码 |
|---|---|
| 文档加载 (Loader) | `rag/loader.py` |
| 文本切分 (Chunker) | `rag/chunker.py`（LangChain RecursiveCharacterTextSplitter） |
| 向量化 (Embedding) | `vector_store.py` → `DefaultEmbeddingFunction`（MiniLM-L6-v2） |
| 向量数据库 (VectorDB) | chroma `PersistentClient` |
| 检索器 (Retriever) | `search_vector_db` → `collection.query` |
| 上下文构造 (Context) | `rag_pipeline.retrieve_context` |
| 答案生成 (LLM) | `rag/llm.py` + `main.py` 的 prompt 模板 |