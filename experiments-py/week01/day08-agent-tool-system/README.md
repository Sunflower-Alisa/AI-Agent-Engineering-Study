# Day08 - Agent Tool System（Agent 工具系统 + 反思）

## 结构

```
day08-agent-tool-system/
├── main.py             # 入口：组装所有模块，交互式输入
├── agent.py            # Agent：Plan → Act → Evaluate → Decide → Generate → Reflect
├── planner.py          # Planner：静态（硬编码）/ 动态（LLM 拆解）计划
├── executor.py         # Executor：动作执行（工具 / LLM）+ 步骤模拟
├── evaluator.py        # Evaluator：评估步骤执行结果质量
├── decision.py         # Decision：LLM 决策动作（注入工具列表 + 缓存结果）
├── replanner.py        # Replanner：动作=replan 时重新制定计划
├── actionrouter.py     # ActionRouter：把步骤路由到 tool / llm 动作
├── generator.py        # AnswerGenerator：汇总执行结果生成最终答案
├── reflection/         # 反思模块
│   ├── evaluator.py    # Reflection_Evaluator：答案质量评分 0-10
│   └── improver.py     # Improver：评分低于阈值时改进答案
├── memory.py           # Memory：短期记忆（最近 5 条执行记录），供 Planner 参考
├── models.py           # pydantic 模型（含 ReflectionResult / ActionModel）
├── llm.py              # LLM 封装：chat + parse_json（统一 venv + config.py）
├── state.py            # AgentState：目标/步骤/观察/评估/缓存/最终答案
└── tools/              # 工具系统
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
                    │ ActionRouter 路由│ ← 每步按关键词分派工具/LLM
                    └───────┬────────┘
                            ▼
                    ┌────────────────┐
                    │ Executor 执行动作 │←──────── 循环
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
     │ 查缓存→执行→  │  │    │    │
     │ 回填→重决策   │  │    │    │
     └──────────────┘  │    │    │
              continue │    │    │ replan
                       ▼    │    ▼
                  ┌────────┐ │ ┌────────────┐
                  │ 记入完成 │ │ │ Replanner  │
                  └────────┘ │ └────────────┘
                             │ finish
                             ▼
                    ┌──────────────────┐
                    │ Generator 生成答案 │  ← 汇总 observations
                    └───────┬──────────┘
                            ▼
                   ┌──────────────────┐
                   │ Reflection 评分   │  0-10，< 阈值则改进
                   └───────┬──────────┘
                           ▼
                       返回最终答案
```

1. **Plan**: `planner.py` `create_plan_dynamic(goal, history)` 先取 `memory.retrieve()`（最近 5 条历史记录），将目标与历史一并交给 LLM 拆解为有序步骤列表，避免重复已完成步骤
2. **Route**: `actionrouter.py` 对**每个当前步骤**按关键词路由——含「搜索/收集资料」→ `search` 工具；含「计算」→ `calculator` 工具；否则走 LLM
3. **Execute**: `executor.py` 执行动作——工具动作走 `execute_tool`（经 `agent._run_tool` 缓存），LLM 动作走 `execute_llm(action.prompt)`；`execute_step` 为遗留的步骤模拟桩
4. **Evaluate**: `evaluator.py` 评估结果（`issues` 非空即建议 replan）
5. **Decide**: `decision.py` 把 `目标 + 当前步骤 + 观察 + 评估 + 已完成计算结果 + 工具列表` 交给 LLM，返回动作 JSON
6. **按动作分发**（`agent.py`）：
   - `tool` → 查 `state.tool_results` 缓存，命中复用；未命中才执行并缓存，回填 `state.observation` 后**原地重决策**
   - `continue` → 弹出步骤，记入 `completed`
   - `replan` → 弹出步骤，记入 `failed`，调用 `replanner.py` 生成新计划
   - `finish` → 结束循环
7. **生成 + 反思**（Day9）：
   - `generator.generate(state)` 汇总 `state.observations` 生成最终答案
   - `reflection/evaluator.py` 对答案评分 0-10
   - 评分 < `reflection_threshold`(8) → `reflection/improver.py` 按问题清单改进答案
   - 返回最终答案

## 决策动作（Decision Action）

`models.py` 中 `Decision.action` 用 `Literal` 限定四种动作：

| 动作 | 含义 | 处理位置 |
|---|---|---|
| `continue` | 本步成功，继续下一步 | `agent.py` 记入 `completed` |
| `tool` | 调用工具获取信息 | `executor.execute_tool` → 结果回填重决策 |
| `replan` | 当前计划需调整 | `replanner.py` 重新生成步骤 |
| `finish` | 目标已达成，结束 | `agent.py` break 跳出循环 |

## 防重复计算机制

`tool` 动作是「执行 → 回填 → 原地重决策」，若 LLM 意识不到答案已在手里，可能对同一计算反复调用。三层保护：

| 机制 | 位置 | 作用 |
|---|---|---|
| **结果缓存** | `agent.py` `_run_tool()` + `state.tool_results` | 路由动作与 Decision 的 tool 动作**统一走同一缓存入口**，相同 `(工具, 参数)` 命中缓存则复用结果，**不再重复执行工具** |
| **决策规则** | `decision.py` prompt | 明确「观察/缓存已含答案 → 禁止重复调用工具」 |
| **单步工具上限** | `agent.py` `MAX_TOOL_PER_STEP=3` | 同一步骤工具请求超过 3 次强制完成该步，杜绝死循环 |

> 工具结果以 `[calculator] 20` 形式回填（`executor.py`），让 LLM 能明确该结果属于哪次计算。

## 反思模块（reflection/）

| 文件 | 作用 |
|---|---|
| `evaluator.py` | `Reflection_Evaluator.evaluate_answer(question, answer)` → LLM 返回 `score(0-10)` + `issues[]` |
| `improver.py` | `Improver.improve_answer(question, answer, issues)` → 按问题清单重新生成优化答案 |

## 记忆模块（memory.py）

`Agent.__init__` 创建 `Memory()` 短期记忆，记录每次任务的执行结果，供下一次 Planner 规划时参考：

| 方法 | 作用 |
|---|---|
| `save(data)` | 在一次任务结束后，把 `{goal, completed, failed, observations, reflection, final_answer}` 追加进短期记忆 |
| `retrieve()` | 返回最近 5 条历史记录，注入 `planner.create_plan_dynamic(goal, history)` 作为规划上下文 |

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
3. **pydantic 对象传参**：各模型均为 `BaseModel`，用属性访问（`observation.issues`、`decision.action`、`action.type`）
4. **防死循环**：`Agent` 默认 `max_steps=30` + 单步工具上限 `MAX_TOOL_PER_STEP=3`，双重兜底避免 replan / tool 反复触发
5. **反思改进**：答案评分低于 `reflection_threshold`(8) 才触发 `Improver`，避免每次生成都做冗余改进
6. **工具循环代价**：`tool` 动作会原地重决策（每轮一次 LLM），结果缓存避免重复执行，但工具循环本身仍有多次 LLM 调用开销
7. **每步都重新路由**：`agent.py` 每次循环对**当前步骤**调用 `actionrouter.route(step)` 生成动作（工具走 `_run_tool` 缓存，避免与 Decision 重复执行同一个工具）；`execute_llm` 传入的是 `action.prompt`（字符串），不要把 `ActionModel` 对象直接当 LLM content
8. **短期记忆**：`memory.py` 为进程内列表（取最近 5 条），未持久化；规划时借助历史避免重复已完成步骤

## 知识点对应

本示例对应 **AI Agent 工具调用 + 反思（Tool Calling / ReAct / Reflection）** 模块知识：

| 概念 | 对应代码 |
|---|---|
| 工具抽象与注册 (Tool Abstraction & Registry) | `tools/base.py` + `tools/registry.py` |
| 工具实现 | `tools/calculator.py`（安全求值）、`tools/search.py` |
| 动作路由 (Action Routing) | `actionrouter.py` → 步骤按关键词路由到 tool / llm |
| 工具选择 (Tool Selection) | `decision.py` → LLM 返回 `tool` + `args` |
| 工具执行与结果回填 (Tool Execution) | `agent._run_tool` → `executor.execute_tool` → 回填 `state.observation` 后重决策 |
| 结果缓存与防重复计算 | `state.tool_results` + `agent.py` 缓存命中 + `MAX_TOOL_PER_STEP` |
| 结果生成 (Answer Generation) | `generator.py` → 汇总执行结果生成最终答案 |
| 反思评分 (Reflection) | `reflection/evaluator.py` → 答案质量评分 0-10 |
| 改进答案 (Improvement) | `reflection/improver.py` → 低于阈值时改进 |
| 记忆 (Memory) | `memory.py` → 短期记忆最近 5 条，注入 `planner.create_plan_dynamic` |
| 行动决策 (Action Selection) | `decision.py` → continue/tool/replan/finish |
| 失败处理与重规划 (Replanning) | `replanner.py` → 动作=replan 时重新生成步骤 |
| Agent 状态跟踪 (State Tracking) | `state.py` → 维护目标/步骤/观察/评估/缓存/答案 |
