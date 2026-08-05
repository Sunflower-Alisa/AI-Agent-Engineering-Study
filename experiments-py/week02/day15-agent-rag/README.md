# Day15 - Agent + RAG（工具系统 + 反思 + 记忆 + 上下文管理 + RAG 知识库 Agent）

综合 **day08（Agent 工具系统 + 反思）/ day11（RAG 知识库）/ day03（记忆）** 的完整 Agent：上下文管理 → 动态规划 → 逐步决策执行 → 反思改进 → 短期/长期记忆持久化，并将 RAG 以 `knowledge_search` 工具形式接入 Agent Loop。

## 整体流程

```
用户目标
  │
  ▼
1. 长期记忆检索（LongMemory.retrieve，取用户历史长期记忆）
2. 知识库上下文初始化（knowledge_context，后续由 knowledge_search 累积）
  │
  ▼
ContextManager.build_context（汇总：用户问题 + 历史对话 + 长期记忆 + 知识库信息）
  │
  ▼
Planner.create_plan_dynamic（结合上下文动态拆解为可执行步骤）
  │
  ▼ ───────── Agent Loop（逐步骤循环）─────────
  │   Decision.decide_currentstep  →  三种动作：
  │     ├─ tool    → 执行工具（结果入 observation；
  │     │            若是 knowledge_search，结果并入 knowledge_context）
  │     ├─ llm     → 直接由 LLM 完成当前步骤
  │     └─ replan  → 步骤无法执行，触发重新规划
  │   每轮结束后无条件弹出当前步骤
  │ ──────────────────────────────────────────
  │
  ▼
Generator 生成最终答案
  │
  ▼
Reflection 打分（0-10）→ 低于阈值(8) 时 Improver 按 issues 自动改进
  │
  ▼
ShortMemory 保存本轮记录 → MemoryExtractor 提取沉淀 → LongMemory 长期持久化
  ↓
输出最终答案
```

## 结构

```
day15-rag-agent/
├── main.py               # 入口：构建 RAG 知识库 → 组装各模块 → 交互式运行 Agent
├── __init__.py
├── llm.py                # LLM 封装：chat（统一 config.py，空/None 内容自动重试）、parse_json
├── models.py             # pydantic 数据模型（Plan/Evaluation/Execution/Decision/ReflectionResult/Action）
├── state.py              # AgentState：目标、步骤、观察、评估、memory_context、knowledge_context、工具缓存
├── actionrouter.py       # 规则路由（含搜索/收集资料/计算等关键词→工具）【当前 Agent Loop 未使用】
├── generator.py          # AnswerGenerator：把执行结果/观察汇总为最终答案
├── agent/                # Agent 核心模块
│   ├── __init__.py
│   ├── agent.py          # Agent 编排：上下文→规划→决策执行→生成→反思→记忆；工具缓存
│   ├── planner.py        # Planner：create_plan_dynamic(goal, context) 动态规划
│   ├── executor.py       # Executor：execute_llm / execute_tool（错误捕获、参数提示）
│   ├── decision.py       # Decision：decide_currentstep（tool/llm/replan）；decide_nextstep（未使用）
│   ├── evaluator.py      # Evaluator：按 observation.issues 判断是否需要 replan
│   └── replanner.py      # Replanner：replan_dynamic 重新生成未完成步骤
├── context/              # 上下文管理（Day17）
│   ├── __init__.py
│   └── manager.py        # ContextManager.build_context：拼装问题+历史+记忆+知识库
├── reflection/           # 反思改进
│   ├── __init__.py
│   ├── evaluator.py      # Reflection_Evaluator：答案打分（0-10）
│   └── improver.py       # Improver：按 issues 改进答案
├── memory/               # 记忆（Day10 短期 / Day17 长期）
│   ├── __init__.py
│   ├── short_memory.py   # ShortMemory：进程内存短期记忆（retrieve 取最近 5 条）
│   ├── long_memory.py    # LongMemory：chroma 持久化长期记忆（./chroma_data，MD5 伪向量）
│   └── extractor.py      # MemoryExtractor：提取值得长期保存的信息（当前为占位实现）
├── rag/                  # RAG 知识库管线
│   ├── __init__.py
│   ├── loader.py         # Loader：读取 md/txt
│   ├── chunker.py        # Chunk：LangChain RecursiveCharacterTextSplitter（chunk_size+overlap）
│   ├── embedding.py      # Embedding：chroma DefaultEmbeddingFunction（ONNX MiniLM-L6-v2）+ 持久化集合
│   ├── vector_store.py   # VectorDB：add_chunks（upsert）/ clear / search（相似度检索）
│   ├── retriever.py      # Retriever：retrieve_context 拼上下文
│   └── rag_pipeline.py   # build_knowledge_base / build_knowledge_base_from_project
├── tools/                # 工具系统
│   ├── __init__.py
│   ├── base.py           # Tool 抽象基类（name / description / run）
│   ├── calculator.py     # Calculator：AST 安全数学计算
│   ├── search.py         # SearchTool：搜索（当前为 mock）
│   ├── knowledge.py      # Knowledge：检索向量知识库 → 返回相关资料上下文
│   └── registry.py       # TOOLS 注册表：calculator / search / knowledge_search
├── documents/
│   └── agent.md          # 示例知识文档（构建知识库的语料）
├── chroma_db/            # RAG 向量数据库持久化目录（运行时生成，已 gitignore）
└── chroma_data/          # LongMemory 长期记忆持久化目录（运行时生成，已 gitignore）
```

## 工具注册表

`tools/registry.py` 统一暴露三个工具，供 Decision 按 `name` 调用：

| 工具名 | 实现类 | 作用 |
|---|---|---|
| `calculator` | `tools/calculator.py` | AST 安全解析数学表达式（含 + - * / 等） |
| `search` | `tools/search.py` | 互联网搜索（当前为 mock，返回固定格式） |
| `knowledge_search` | `tools/knowledge.py` | RAG 工具：对 query 检索向量知识库，返回相关文本片段做上下文 |

`knowledge_search` 调用 `rag/vector_store.search_vector_db` 完成相似度检索，把 RAG 以“工具”形式接入 Agent Loop。

## Agent Loop 要点

1. **决策驱动执行**：`Decision.decide_currentstep` 只针对**当前步骤**做执行决策（不规划新步骤、不判断是否结束），返回 `tool` / `llm` / `replan` 三种动作之一（`agent.py:81`）。
2. **工具缓存**：`_run_tool` 以 `(name, 规范化后的 args)` 为 key 缓存结果（`agent.py:47-57`），同参命中不重复执行。
3. **RAG 上下文累积**：当决策为 `tool` 且工具是 `knowledge_search` 时，检索结果并入 `state.knowledge_context`（`agent.py:95-103`），供后续决策/生成复用；否则作为普通 observation 记录。
4. **重新规划**：`replan` 时由 `Replanner.replan_dynamic(state, context, reason)` 按当前上下文/观察重新生成 `steps`（`agent.py:90-91`）。
5. **反思改进**：答案生成后 `Reflection_Evaluator` 打分，`score < 8` 时由 `Improver` 按 issues 改进（`agent.py:153-156`）。
6. **记忆沉淀**：每轮存入 `ShortMemory`（最近 5 条）；`LongMemory.retrieve` 供下轮规划前取回；`MemoryExtractor` 负责提炼长期记忆（当前为占位）。

## 运行

```bash
cd experiments-py/week02/day15-rag-agent
..\..\.venv\Scripts\python.exe main.py
```

> - 需要 `DEEPSEEK_API_KEY` 环境变量（统一 `experiments-py/config.py`）
> - 启动时 `build_knowledge_base_from_project()` 加载 `documents/agent.md` → 切块 → 向量化入库（`chroma_db/`）
> - 首次运行 chroma 会下载 MiniLM 嵌入模型（约 79MB）到 `~/.cache/chroma/onnx_models/`，仅一次；断网/慢速参考 day11 README 的 `curl -C -` 续传方案

## 重点注意事项

1. **空响应重试**：`deepseek-v4-flash` 是推理型模型，偶发 `content=None`/空。`llm.py` 的 `chat` 已加 `max_tokens=2048` 并在空内容时自动重试（默认 3 次），仍失败抛 `RuntimeError`——避免空字符串传入 `parse_json` 崩溃。
2. **绝对导入 + `__init__.py`**：各子包均需 `__init__.py`；内部统一用绝对导入（如 `from tools.registry import TOOLS` ）。直接运行 `main.py` 时其顶部 `sys.path.insert` 已注入项目根目录；`config.py` 由 venv 的 `experiments.pth` 自动引入。
3. **长期记忆免下载**：`LongMemory` 用基于 MD5 哈希的确定性伪随机向量（`memory/long_memory.py:13-19`），不需要下载嵌入模型；持久化到 `./chroma_data`（相对 CWD）。RAG 知识库用真正的语义嵌入（`chroma_db/`）。
4. **工具需 description**：`Tool` 子类必须有 `name` 与 `description` 属性，否则决策 prompt 与错误提示会取到空值。
5. **Python 3.9 兼容**：类型标注用 `Optional[str]`，不用 `str | None`（PEP 604 需 3.10+）。
6. **控制台编码**：Windows 控制台默认 GBK，print 中避免 emoji（如 `✅`），否则报 `UnicodeEncodeError`。
7. **循环导入**：RAG 向量库只放“数据+查询”，构建/检索管线独立在 `rag_pipeline.py`，避免 `embedding ↔ vector_store` 循环。
8. **遗留项**：`ActionRouter`、`MAX_TOOL_PER_STEP`、`Decide.decide_nextstep` 在最新 `agent.py` 中已被注释/未调用；`state.py` 中 `knowlege_context`（拼写笔误）由 `agent.py` 动态设置的 `knowledge_context` 替代。

## 知识点对应

| 概念 | 对应代码 |
|---|---|
| 上下文管理 Context | `context/manager.py` |
| 规划 Planning | `agent/planner.py`、`agent/replanner.py` |
| 执行 Execution | `agent/executor.py` |
| 决策 Decision | `agent/decision.py`（decide_currentstep：tool/llm/replan） |
| 工具调用 Tool Calling | `tools/registry.py` + `agent/executor.py` |
| 反思 Reflection | `reflection/evaluator.py` + `reflection/improver.py` |
| 记忆 Memory | `memory/short_memory.py` + `memory/long_memory.py` + `memory/extractor.py` |
| RAG 检索增强生成 | `rag/*`（loader → chunker → embedding → vector_store → retriever） |
| RAG 作工具接入 | `tools/knowledge.py` → `rag.vector_store.search_vector_db` |