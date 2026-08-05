# Day15 - Agent + RAG（工具系统 + 反思 + RAG 知识库 Agent）

综合 **day08（Agent 工具系统 + 反思）** 与 **day11（RAG 知识库）** 的完整 Agent 实现：规划 → 执行 → 评估 → 决策 → 重规划 → 生成答案 → 反思 → 改进，并集成短期记忆与基于向量检索的 `knowledge_search` 工具。

## 整体流程

```
用户目标
  │
  ▼
Planner 规划（结合历史记忆动态拆解可执行步骤）
  │
  ▼ ─────────── Agent Loop（每一步重复）───────────
  │    执行工具 / LLM  →  观察  →  评估  →  决策
  │    （ActionRouter 路由；工具结果缓存，同参不重复执行）
  │    Decision：continue / tool / replan / finish
  │ ──────────────────────────────────────────────
  │
  ▼ 步骤全部完成
Generator 生成最终答案
  │
  ▼
Reflection 质量打分（0-10）→ 低于阈值时 Improver 自动改进
  │
  ▼
Memory 保存本轮记录（供下轮规划参考）
  ↓
输出最终答案
```

## 结构

```
day15-rag-agent/
├── main.py              # 入口：构建 RAG 知识库 → 交互式输入 → 运行 Agent
├── __init__.py
├── llm.py               # LLM 封装：chat（统一 config.py，空/None 内容自动重试）、parse_json
├── models.py            # pydantic 数据模型（Plan/Evaluation/Execution/Decision/ReflectionResult/Action）
├── state.py             # AgentState：目标、步骤、观察、评估、工具结果缓存
├── actionrouter.py      # 规则路由：含"搜索/计算"关键词的步骤 → 工具，否则 LLM 生成
├── generator.py         # AnswerGenerator：把执行结果/观察汇总为最终答案
├── agent/               # Agent 核心模块
│   ├── __init__.py
│   ├── agent.py         # Agent 编排：规划→执行→评估→决策→重规划→生成→反思→改进；工具缓存
│   ├── planner.py       # Planner：静态/动态（按历史记忆）规划
│   ├── executor.py      # Executor：execute_llm / execute_tool（错误捕获、参数提示）
│   ├── decision.py      # Decision：LLM 决策（continue/tool/replan/finish）
│   ├── evaluator.py     # Evaluator：评估当前步骤结果
│   └── replanner.py     # Replanner：失败/需调整时重新规划
├── reflection/          # 反思改进
│   ├── __init__.py
│   ├── evaluator.py     # Reflection_Evaluator：答案打分（0-10）
│   └── improver.py      # Improver：按 issues 改进答案
├── memory/
│   ├── __init__.py
│   └── memory.py        # Memory：短期记忆（retrieve 最近 5 条）
├── rag/                 # RAG 知识库管线
│   ├── __init__.py
│   ├── loader.py        # Loader：读取 md/txt
│   ├── chunker.py       # Chunk：LangChain RecursiveCharacterTextSplitter
│   ├── embedding.py     # Embedding：chroma DefaultEmbeddingFunction（ONNX MiniLM-L6-v2）+ 持久化集合
│   ├── vector_store.py  # VectorDB：add_chunks（upsert）/ clear / search（相似度检索）
│   ├── retriever.py     # Retriever：retrieve_context 拼上下文
│   └── rag_pipeline.py  # build_knowledge_base / build_knowledge_base_from_project
├── tools/               # 工具系统
│   ├── __init__.py
│   ├── base.py          # Tool 抽象基类（name / description / run）
│   ├── calculator.py    # Calculator：AST 安全数学计算
│   ├── search.py        # SearchTool：搜索（当前为 mock）
│   ├── knowledge.py     # Knowledge：检索向量知识库 → 返回相关资料上下文
│   └── registry.py      # TOOLS 注册表：calculator / search / knowledge_search
├── documents/
│   └── agent.md         # 示例知识文档（构建知识库的语料）
└── chroma_db/           # 向量数据库持久化目录（运行时生成，已 gitignore）
```

## 工具注册表

`tools/registry.py` 统一暴露三个工具，供 ActionRouter 与 Decision 按 `name` 调用：

| 工具名 | 实现类 | 作用 |
|---|---|---|
| `calculator` | `tools/calculator.py` | AST 安全解析数学表达式（含 + - * / 等） |
| `search` | `tools/search.py` | 互联网搜索（当前为 mock，返回固定格式） |
| `knowledge_search` | `tools/knowledge.py` | RAG 工具：对 query 检索向量知识库，返回相关文本片段做上下文 |

`knowledge_search` 调用 `rag/vector_store.search_vector_db` 完成相似度检索，把 RAG 以“工具”形式接入 Agent Loop。

## Agent Loop 要点

1. **每步重路由**：每一步都重新经过 `ActionRouter.route` 决定动作（`agent.py:63`），而非仅在首轮路由。带“搜索/计算”关键词的步骤走工具，其余走 LLM 生成。
2. **工具缓存**：`_run_tool` 以 `(name, 规范化后的 args)` 为 key 缓存结果（`agent.py:39-49`），命中缓存不重复执行，避免 LLM 反复调用同一工具。
3. **决策动作**：`Decision.decide` → `DecisionModel.action` 之一，决定继续 / 调用工具 / 重新规划 / 结束。
4. **工具调用上限**：同一步最多 `MAX_TOOL_PER_STEP=3` 次，防止工具死循环（`agent.py:82-88`）。
5. **反思改进**：答案生成后 `Reflection_Evaluator` 打分，`score < 8` 时由 `Improver` 按 issues 改进（`agent.py:126-127`）。

## 运行

```bash
cd experiments-py/week02/day15-rag-agent
..\..\.venv\Scripts\python.exe main.py
```

> - 需要 `DEEPSEEK_API_KEY` 环境变量（统一 `experiments-py/config.py`）
> - 启动时 `build_knowledge_base_from_project()` 加载 `documents/agent.md` → 切块 → 向量化入库，首个请求检索 `knowledge_search`
> - 首次运行 chroma 会下载 MiniLM 嵌入模型（约 79MB）到 `~/.cache/chroma/onnx_models/`，仅一次；断网/慢速参考 day11 README 的 `curl -C -` 续传方案

## 重点注意事项

1. **空响应重试**：`deepseek-v4-flash` 是推理型模型，偶发 `content=None`/空。`llm.py` 的 `chat` 已加 `max_tokens=2048` 并在空内容时自动重试（默认 3 次），仍失败抛 `RuntimeError`——避免空字符串传入 `parse_json` 崩溃。
2. **绝对导入 + `__init__.py`**：各子包均需 `__init__.py`；内部统一用绝对导入（如 `from tools.registry import TOOLS`）。直接运行 `main.py` 时其顶部 `sys.path.insert` 已注入项目根目录；`config.py` 由 venv 的 `experiments.pth` 自动引入。
3. **循环导入**：向量库只放“数据+查询”，构建/检索管线独立在 `rag_pipeline.py`，避免 `embedding ↔ vector_store` 循环。
4. **工具需 description**：`Tool` 子类必须有 `name` 与 `description` 属性，否则决策 prompt 与错误提示会取到空值。
5. **Python 3.9 兼容**：类型标注用 `Optional[str]`，不用 `str | None`（PEP 604 需 3.10+）。
6. **控制台编码**：Windows 控制台默认 GBK，print 中避免 emoji（如 `✅`），否则报 `UnicodeEncodeError`。
7. **数据目录**：chroma 持久化用 `Path(__file__)` 定位到项目 `./chroma_db`，与 CWD 无关。

## 知识点对应

| 概念 | 对应代码 |
|---|---|
| 规划 Planning | `agent/planner.py`、`agent/replanner.py` |
| 执行 Execution | `agent/executor.py` |
| 决策 Decision | `agent/decision.py`（continue/tool/replan/finish） |
| 工具调用 Tool Calling | `actionrouter.py` + `tools/registry.py` |
| 反思 Reflection | `reflection/evaluator.py` + `reflection/improver.py` |
| 记忆 Memory | `memory/memory.py`（短期，取最近 5 条） |
| RAG 检索增强生成 | `rag/*`（loader → chunker → embedding → vector_store → retriever） |
| RAG 作工具接入 | `tools/knowledge.py` → `rag.vector_store.search_vector_db` |