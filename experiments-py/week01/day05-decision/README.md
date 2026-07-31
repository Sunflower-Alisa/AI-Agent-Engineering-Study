# Day05 - Decision（决策与行动选择）

## 结构

```
day05-decision/
├── main.py        # 入口：Plan → Execute → Evaluate → Decide 循环
├── state.py       # AgentState：目标、步骤、观察结果、评估结果、下一动作
├── planner.py     # 计划生成：静态（硬编码） / 动态（LLM 拆解目标）
├── executor.py    # 步骤执行器：模拟执行，可返回问题触发重规划
├── evaluator.py   # 评估器：判断执行结果质量
├── decision.py    # 决策器：LLM 根据当前状态选择下一步动作（Think）
├── replanner.py   # 重规划器：动作=replan 时重新制定后续计划
├── models.py      # pydantic 数据模型：Plan / Evaluation / Execution / Decision
├── llm.py         # LLM 调用封装（从统一 venv + config.py 读取）
└── tools/         # 预留工具目录（tool 动作的扩展位，当前为空）
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
                    │ Executor 执行步 │←───── 循环
                    └───────┬────────┘
                            ▼
                   ┌──────────────────┐
                   │ Evaluator 评估结果 │
                   └───────┬──────────┘
                           ▼
                   ┌──────────────────┐
                   │ Decision 决策动作 │  ← LLM 选择下一步
                   └───┬────┬────┬────┘
              continue │    │    │ replan
                       ▼    │    ▼
                  ┌────────┐ │ ┌────────────┐
                  │ 记入完成 │ │ │ Replanner  │
                  │ 继续下一步│ │ │ 重新规划    │
                  └────────┘ │ └────────────┘
                             │ finish
                             ▼
                       ┌──────────┐
                       │ 结束整个  │
                       │ 任务     │
                       └──────────┘
```

1. **Plan**: `planner.py` 将目标拆解为有序步骤列表
2. **Execute**: `executor.py` 依次执行当前步骤，返回观察结果
3. **Evaluate**: `evaluator.py` 评估执行结果质量（成功/存在问题）
4. **Decide**: `decision.py` 将 `目标 + 当前步骤 + 观察结果` 交给 LLM，让它选择下一步动作
5. **按动作分支**：`main.py` 根据决策分发
   - `continue` → 记入完成，继续下一个步骤
   - `replan` → 调用 `replanner.py` 重新生成计划
   - `finish` → 提前结束整个任务
   - `tool` → 预留：需要调用外部工具时选择（当前未接入，见 `tools/`）

## 决策动作（Decision Action）

`models.py` 中 `Decision.action` 使用 `Literal` 限定四种动作：

| 动作 | 含义 | 触发处理 |
|---|---|---|
| `continue` | 本步成功，继续下一步 | `main.py` 记入 `completed` |
| `tool` | 需要调用工具获取信息 | 预留，`tools/` 目录待扩展 |
| `replan` | 当前计划需调整 | `replanner.py` 重新生成步骤 |
| `finish` | 目标已达成，提前结束 | `main.py` break 跳出循环 |

> 与 Day04 相比，本示例把「是否继续 / 是否重规划」的判断从写死代码（`evaluator` 硬编码判断）升级为 **LLM 决策**：`decision.py` 依据完整的 Agent 状态（目标、当前步骤、观察）在四种动作中自主选择。

## 运行

```bash
..\..\.venv\Scripts\python.exe main.py
```

> 统一使用 `experiments-py/.venv`，通过 `.pth` 自动引入 `config.py`，各脚本不需要手动配置 sys.path。

## 重点注意事项

1. **统一虚拟环境**：所有 day 共用 `experiments-py/.venv`，通过 `.pth` 自动引入 `config.py`
2. **启用了动态规划**：代码同时保留 `create_plan_static` / `replan_static` 作为静态版本对照，当前注释掉静态版本
3. **数据模型统一用 pydantic**：`Execution` / `Evaluation` / `Decision` / `Plan` 均为 `BaseModel`，各模块间通过对象（而非 dict）传参，注意用属性访问（`observation.issues`、`decision.action`）
4. **`tool` 动作是扩展位**：`models.py` 已定义该动作、`tools/` 目录已预留，但尚未实现工具执行逻辑，可自行扩展

## 知识点对应

本示例对应 **AI Agent 决策（Decision Making）** 模块知识：

| 概念 | 对应代码 |
|---|---|
| 目标拆解 (Task Decomposition) | `planner.py` → LLM 将用户目标拆为子步骤 |
| 顺序执行 (Sequential Execution) | `main.py` while 循环 `pop(0)` 逐项执行 |
| 结果评估 (Evaluation) | `evaluator.py` → 评估执行结果质量 |
| 行动决策 (Action Selection) | `decision.py` → LLM 在 continue/tool/replan/finish 中选择 |
| 失败处理与重规划 (Replanning) | `replanner.py` → 动作=replan 时重新生成步骤列表 |
| Agent 状态跟踪 (State Tracking) | `state.py` → 维护目标/步骤/观察/评估/下一动作 |
