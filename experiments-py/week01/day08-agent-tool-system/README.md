# Day08 - Agent Tool System（Agent 工具系统）

## 结构

```
day08-agent-tool-system/
├── main.py        # 入口：组装各模块，交互式输入
├── agent.py       # Agent：Plan → Act → Evaluate → Decide 循环 + 动作分发
├── planner.py     # Planner：静态（硬编码）/ 动态（LLM 拆解目标）计划
├── executor.py    # Executor：步骤执行（模拟）+ 工具调用（走 TOOLS 注册表）
├── evaluator.py   # Evaluator：评估执行结果质量
├── decision.py    # Decision：LLM 依据状态选择动作（注入可用工具列表）
├── replanner.py   # Replanner：动作=replan 时重新制定计划
├── models.py      # pydantic 模型：Plan / Evaluation / Execution / Decision
├── llm.py         # LLM 封装：chat + parse_json（统一 venv + config.py）
├── state.py       # AgentState：目标/步骤/观察/评估/下一动作
└── tools/         # 工具系统
    ├── base.py        # Tool 抽象基类（run 接口）
    ├── registry.py    # TOOLS 注册表：name → 工具实例
    ├── calculator.py  # 计算器工具（基于 ast 的安全求值，不用 eval）
    └── search.py      # 搜索工具（模拟返回结果）
```

## 运行逻辑

```
                          ┌─────────────┐
                          │   目标 Goal  │
                          └──────┬──────┘
                                 ▼
                     ┌───────────────────┐
                     │  Planner 拆解步骤  │
                     └───────┬───────────┘
                             ▼
                    ┌────────────────┐
                    │ Executor 执行步 │←──────────── 循环
                    └───────┬────────┘
                            ▼
                   ┌──────────────────┐
                   │ Evaluator 评估结果 │
                   └───────┬──────────┘
                           ▼
                   ┌──────────────────┐
                   │ Decision 决策动作 │  ← LLM 选择
                   └──┬────┬────┬─────┘
              tool     │    │    │
              ▼        │    │    │
     ┌──────────────┐  │    │    │
     │ execute_tool │  │    │    │
     │ 结果回填后    │  │    │    │
     │ 重新决策      │  │    │    │
     └──────────────┘  │    │    │
              continue │    │    │ replan
                       ▼    │    ▼
                  ┌────────┐ │ ┌────────────┐
                  │ 记入完成 │ │ │ Replanner  │
                  │ 继续下一步│ │ │ 重新规划    │
                  └────────┘ │ └────────────┘
                             │ finish
                             ▼
                       ┌──────────┐
                       │ 结束任务  │
                       └──────────┘
```

1. **Plan**: `planner.py` 将目标拆解为有序步骤列表
2. **Execute**: `executor.py` 执行当前步骤（模拟执行）
3. **Evaluate**: `evaluator.py` 评估结果（`issues` 非空即建议重规划）
4. **Decide**: `decision.py` 把 `目标 + 当前步骤 + 观察结果 + 评估结果 + 可用工具列表` 交给 LLM，返回动作 JSON
5. **按动作分发**（`agent.py`）：
   - `tool` → `execute_tool` 调用工具，结果回填 `state.observation` 后**原地重新决策**（不推进步骤）
   - `continue` → 弹出步骤，记入 `completed`
   - `replan` → 弹出步骤，记入 `failed`，调用 `replanner.py` 生成新计划
   - `finish` → 提前结束任务

## 决策动作（Decision Action）

`models.py` 中 `Decision.action` 用 `Literal` 限定四种动作，`tool`/`args`/`reason` 为可选字段：

| 动作 | 含义 | 处理位置 |
|---|---|---|
| `continue` | 本步成功，继续下一步 | `agent.py` 记入 `completed` |
| `tool` | 调用工具获取信息 | `executor.execute_tool` → 结果回填重决策 |
| `replan` | 当前计划需调整 | `replanner.py` 重新生成步骤 |
| `finish` | 目标已达成，结束 | `agent.py` break 跳出循环 |

> 相比 Day05：决策模块不再只有空壳，`decision.py` 会把 `TOOLS` 注册表（工具名 + 描述）注入 prompt，LLM 可选对工具并返回 `tool` + `args`，真正打通 Think → Act(Tool) → Observe → Think 的闭环。

## 工具系统（tools/）

- **`base.py`**：`Tool` 抽象基类，子类实现 `run(**kwargs)`
- **`registry.py`**：`TOOLS = {"calculator": ..., "search": ...}`，新增工具只需实现 `Tool` 并注册
- **`calculator.py`**：`run(expression)`，用 `ast` 白名单安全求值（只支持四则/乘方/取模/一元运算），**不使用 `eval`**，恶意表达式返回错误信息
- **`search.py`**：`run(query)`，模拟返回 `搜索结果：{query}`

## 运行

```bash
..\..\.venv\Scripts\python.exe main.py
```

> 统一使用 `experiments-py/.venv`，通过 `.pth` 自动引入 `config.py`；需要 `DEEPSEEK_API_KEY` 环境变量。

## 重点注意事项

1. **统一虚拟环境**：所有 day 共用 `experiments-py/.venv`，无需手动配置 sys.path
2. **Python 3.9 兼容**：venv 是 3.9，`Optional[str]` 写法不能用 `str | None`（PEP 604 需 3.10+）
3. **pydantic 对象传参**：`Execution`/`Evaluation`/`Decision`/`Plan` 均为 `BaseModel`，用属性访问（`observation.issues`、`decision.action`）
4. **防死循环**：`Agent` 默认 `max_steps=30`，避免 replan / tool 反复触发导致死循环
5. **工具循环代价**：`tool` 动作会原地重决策，若 LLM 反复选同一工具会多次调用——这是 LLM 决策系统的已知权衡，可在决策 prompt 中提示「观察结果已含答案则不要重复调用工具」

## 知识点对应

本示例对应 **AI Agent 工具调用（Tool Calling / ReAct）** 模块知识：

| 概念 | 对应代码 |
|---|---|
| 工具抽象与注册 (Tool Abstraction & Registry) | `tools/base.py` + `tools/registry.py` |
| 工具实现 | `tools/calculator.py`（安全求值）、`tools/search.py` |
| 工具选择 (Tool Selection) | `decision.py` → LLM 返回 `tool` + `args` |
| 工具执行与结果回填 (Tool Execution) | `executor.execute_tool` → 回填 `state.observation` 后重决策 |
| 行动决策 (Action Selection) | `decision.py` → continue/tool/replan/finish |
| 失败处理与重规划 (Replanning) | `replanner.py` → 动作=replan 时重新生成步骤 |
| Agent 状态跟踪 (State Tracking) | `state.py` → 维护目标/步骤/观察/评估/下一动作 |
