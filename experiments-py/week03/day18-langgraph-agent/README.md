# Day18 - LangGraph Agent（用 LangGraph 状态图编排 Agent）

基于 **LangGraph `StateGraph`** 实现的 Agent：以“节点 + 有向边 + 条件路由”的方式把 规划 → 决策 → 执行 → 反思 串成一张可执行计算图，通过显式的状态（`AgentState`）在节点间传递数据。

## 执行图

```
(start) app.invoke(AgentState(...))
   │
   ▼
planner ────────────── 生成 steps；current_step = steps[0]
   │
   ▼
decision ── action_router ──────────────────
   │            │              │
 "tool"       "execute"      "replan"
   │            │              │
   ▼            ▼              ▼
executor ◄──────┘              planner   (重新规划)
   │
   ▼
reflection ── result_router ──────────────
   │            │
  success      retry
   │            │
   ▼            ▼
   END         planner   (重试 → 重新规划)
```

## 结构

```
day18-langgraph-agent/
├── main.py               # 入口：create_graph() 构建图 → invoke 初始状态
├── README.md
└── agent/
    ├── __init__.py
    ├── state.py          # AgentState (pydantic)：goal/steps/current_step/observation/evaluation/action/answer/retry_count
    ├── models.py         # DecisionModel（action/tool/args）
    ├── llm.py            # chat / parse_json（统一 config.py）
    ├── prompt.py         # create_planner_prompt / create_decision_prompt / create_reflection_prompt
    ├── nodes.py          # planner_node / executor_node / decision_node / reflection_node
    ├── router.py         # action_router（tool/execute/replan）、result_router（finish/retry）
    └── graph.py          # create_graph：注册节点、入口、普通边与条件边
```

## 流程说明

1. `planner_node`：LLM 根据 `goal` 拆解计划 → 写入 `state.steps`，并取 `steps[0]` 作为 `current_step`。
2. `decision_node`：LLM 对**当前步骤**选择 `tool` / `execute` / `replan`，结果写入 `state.action`。
3. `action_router`：按 `action` 路由 → `tool`/`execute` 都进 `executor`；`replan` 回 `planner`。
4. `executor_node`：执行当前步骤，把结果写入 `state.observation`（当前为模拟执行，无真实工具调用）。
5. `reflection_node`：LLM 评估当前步骤是否成功，结果写入 `state.evaluation`。
6. `result_router`：成功 → `finish`（到 `END`）；否则 → `retry`（回 `planner` 重新规划）。

## 运行

```bash
cd experiments-py/week03/day18-langgraph-agent
..\..\.venv\Scripts\python.exe main.py
```

> - 需要 `DEEPSEEK_API_KEY` 环境变量（统一 `experiments-py/config.py`）
> - 需要安装 `langgraph`（统一 venv 中需存在该依赖）

## 注意事项 / 已知待完善（现状如实）

1. **`AgentState` 必填字段**：`state.py` 中 `evaluation` / `action` 无默认值，但 `main.py` 构造 `AgentState(...)` 未传入 → 现运行会抛 pydantic `ValidationError`。可在 `state.py` 加默认值或在 `main.py` 传入。
2. **`current_step` 不会自动推进**：目前只有 `planner_node` 会写 `current_step`（恒为 `steps[0]`），缺少"当前步成功后推进到下一步"的机制，因此多步骤计划实际只会执行第一步；计划推进 / 步进逻辑需自行补 `step_index` + 推进节点。
3. **`decision` prompt 未给 JSON 模板**：`create_decision_prompt` 只让模型“返回JSON”，未限定结构，且 `state.action = data` 直接把整个字典赋给 `action`（`str` 字段），路由时 `== "tool"` 恒不匹配 → 总是落到 `execute`。
4. **`reflection` 字段拼写**：`reflection_node` 写的是 `state.evalution`（拼写错），与 `state.evaluation` 不一致；`result_router` 直接对 `evaluation["success"]` 取键（该字段类型是 `str`）会报错。
5. **重试语义**：`result_router` 的 `retry` 回到 `planner` 是“整体重新规划、回到第一步”，并非重试当前失败步骤，且无最大迭代保护，存在死循环风险。
6. **`llm.py` 无空响应防护**：相比 day15，未加 `max_tokens` 与空内容重试，偶发空响应会令 `parse_json` 崩溃。

## 知识点对应

| 概念 | 对应代码 |
|---|---|
| 状态图 StateGraph | `agent/graph.py` |
| 节点 Node | `agent/nodes.py`（planner / executor / decision / reflection） |
| 条件路由 Conditional Edge | `agent/router.py`（action_router / result_router） |
| 图状态 State | `agent/state.py` |
| Prompt 构造 | `agent/prompt.py` |
| LLM 调用 | `agent/llm.py` |