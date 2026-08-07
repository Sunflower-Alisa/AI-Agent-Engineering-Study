# Day18 - LangGraph Agent（用 LangGraph 状态图编排 Agent，集成 Tool + RAG）

基于 **LangGraph `StateGraph`** 实现的 Agent：以「节点 + 有向边 + 条件路由」把 任务路由 → 规划 → 决策 → 执行 → 反思 串成可执行计算图，并通过显式状态 `AgentState` 在节点间传递数据。新增统一**工具系统（`tool/`）**与 **RAG 知识库（`rag/`）**，`knowledge_search` 作为工具接入执行器。

## 执行图

```
(start) app.invoke(AgentState(...))     main.py goal="2+3"
   │
   ▼
router ── router_selector（state.router["route"]）────
   │            │
  "tool"      "planner"
   │            │
   ▼            ▼
executor      planner ──→ decision ── action_router ─────────────────
   │               │              │            │            │
   │            replan         "tool"       "execute"     "replan"
   │               │              │            │            │
   │               └──────────────▼◄───────────┘            │
   │                        executor ───────────────────────┘
   ▼
reflection ── result_router ─────────
   │            │
  success      失败/
  "finish"     "retry"
   │            │
   ▼            ▼
   END         planner       <-- step_check（已定义但未接线，见下注）
```

`step_check` 节点 + `step_router`（`len(steps)>0 → continue→decision / finish→END`）已在 `graph.add_node` 定义并设置条件边，但**当前图中没有边指向它**，尚未实际参与循环。

## 结构

```
day18-langgraph-agent/
├── main.py               # 入口：import tool（注册工具）→ create_graph() → invoke 初始状态 → print 结果
├── agent/                # LangGraph 图编排
│   ├── __init__.py
│   ├── graph.py          # create_graph：注册节点、入口、普通边与条件边
│   ├── state.py          # AgentState (pydantic)：goal/steps/current_step/observation/evaluation/action/tool/args/answer/retry_count/next_step/router
│   ├── models.py         # DecisionModel、RouterDecision（router 的 LLM 决策模型）
│   ├── llm.py            # chat / parse_json（统一 config.py）
│   ├── prompt.py         # create_planner/decision/reflection/router 四类 prompt
│   ├── nodes.py          # router_node / planner_node / decision_node / executor_node / reflection_node
│   └── router.py         # router_selector / action_router / result_router / step_router
├── tool/                 # 工具系统（tool + RAG 工具）
│   ├── __init__.py       # 注册 Calculator / Search / KnowledgeSearch（带入 Retriever）
│   ├── base.py           # Tool 抽象基类（name / description / run(args)）
│   ├── registry.py       # TOOLS 注册表：register / get_tool / get_all_tools
│   ├── calculator.py     # CalculatorTool：数学计算（eval）
│   ├── search.py         # SearchTool：搜索（mock，返回固定串）
│   └── knowledge.py      # KnowledgeSearchTool：调用 Retriever 查知识库
├── rag/                  # RAG 知识库管线（持久化于 ./chroma_db）
│   ├── __init__.py
│   ├── loader.py         # 读取 md/txt
│   ├── chunker.py        # LangChain RecursiveCharacterTextSplitter
│   ├── embedding.py      # chroma DefaultEmbeddingFunction（ONNX MiniLM-L6-v2）+ PersistentClient
│   ├── vector_store.py   # add_chunks（upsert）/ clear / search（相似度检索）
│   ├── retriever.py      # Retriever.search(query) → 检索并拼接上下文
│   └── rag_pipeline.py   # build_knowledge_base / build_knowledge_base_from_project
└── README.md
```

## 流程说明（走一遍 goal="2+3"）

1. `router_node`：`create_router_prompt` 让 LLM 决定路线 `tool` / `planner`，用 `RouterDecision` 校验，写入 `state.router`（route/tool/reason），`tool` 时同时写入 `state.action`/`tool`/`args`。`router_selector` 据 `state.router["route"]` 把简单计算直接送去 `executor`，复杂任务送去 `planner`。
2. `executor_node`：`action == "tool"` 时 `get_tool(state.tool)` → `tool.run(state.args)`，结果写入 `observation`；否则按 `retry_count` 模拟成功/失败。
3. `reflection_node`：LLM 评估执行结果（`success`/`reason`），写入 `state.evaluation`（dict）。
4. `result_router`：`evaluation["success"]` 为真 → `finish`（END）；否则 `retry`（回 `planner` 重新规划）。

工具注册后经 `prompt.create_decision_prompt` / `create_router_prompt`（`get_all_tools`）注入 LLM，可在决策/路由中看到并选择。

## 运行

```bash
cd experiments-py/week03/day18-langgraph-agent
..\..\.venv\Scripts\python.exe main.py
```

> - 需要 `DEEPSEEK_API_KEY` 环境变量（统一 `experiments-py/config.py`）
> - 需要安装 `langgraph`、`chromadb`、`langchain-text-splitters`（统一 venv）
> - 默认入口 goal 为 `"2+3"`（走 router→tool→executor→reflection→END）

## 注意事项 / 已知待完善（现状如实）

1. **`step_check`/`step_router` 未接线**：`graph.py` 定义了 `step_check` 节点与 `continue→decision / finish→END` 条件边，但图中没有边进入它，`current_step` 的多步推进会不受触发。
2. **`retry` 语义仍是重新规划**：`result_router` 的 `retry` 回到 `planner`，会重建 `steps` 并取回 `steps[0]`，并非重试当前失败步骤，且无最大迭代保护（`retry_count` 未被递减/判断），存在死循环风险。
3. **工具参数类型不一致**：`RouterDecision.args` 为 `str`，`executor` 以 `tool.run(state.args)` 位置传参。`CalculatorTool.run` 直接 `eval(expression)` OK；但 `KnowledgeSearchTool.run` 内部 `args["query"]` 需 dict，用字符串会下标报错。
4. **`eval` 不够安全**：`CalculatorTool` 用内置 `eval` 执行表达式，存在安全风险（对比 day11/day15 的 AST 安全解析）。
5. **`answer` 尚未填充**：`AgentState.answer` 从未被写入最终答案；`main.py` 打印的是整份 `result` state。
6. **`llm.py` 无空响应防护**：对比 day15，未加 `max_tokens` 与空内容重试，`deepseek-v4-flash` 偶发空响应会使 `parse_json` 崩溃。
7. **`rag/` 未建库**：`tool/__init__.py` 注册了 `KnowledgeSearchTool(Retriever())`，但 `main.py` 未调用 `build_knowledge_base_from_project`（且 day18 无 `documents/agent.md`），知识库为空 → `knowledge_search` 现不会返回资料。

## 知识点对应

| 概念 | 对应代码 |
|---|---|
| 状态图 StateGraph | `agent/graph.py` |
| 节点 Node | `agent/nodes.py`（router / planner / decision / executor / reflection） |
| 条件路由 Conditional Edge | `agent/router.py` |
| 图状态 State | `agent/state.py` |
| Prompt 构造 | `agent/prompt.py` |
| 工具注册/调用 | `tool/`（registry / base / calculator / search / knowledge） |
| RAG 检索增强 | `rag/`（loader → chunker → embedding → vector_store → retriever） |
| LLM 调用 | `agent/llm.py` |