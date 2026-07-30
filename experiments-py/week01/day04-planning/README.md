# Day04 - Planning（计划与重规划）

## 结构

```
day04-planning/
├── main.py        # 入口：Plan → Execute → Evaluate → Replan 循环
├── state.py       # AgentState：目标、步骤列表、完成/失败记录
├── planner.py     # 计划生成：静态（硬编码） / 动态（LLM 拆解目标）
├── executor.py    # 步骤执行器：模拟执行，可返回失败触发重规划
├── evaluator.py   # 评估器：判断执行结果是否需要重规划
├── replanner.py   # 重规划器：失败时重新制定后续计划
└── llm.py         # LLM 调用封装（从统一 venv + config.py 读取）
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
                    │ Executor 执行步 │←── 循环
                    └───────┬────────┘
                            ▼
                   ┌──────────────────┐
                   │ Evaluator 评估结果 │
                   └───┬───────┬──────┘
                  成功 │       │ 需重规划
                       ▼       ▼
                 ┌────────┐ ┌────────────┐
                 │ 继续下一 │ │ Replanner  │
                 │ 步      │ │ 重新规划    │
                 └────────┘ └────────────┘
```

1. **Plan**: `planner.py` 将目标拆解为有序步骤列表
2. **Execute**: `executor.py` 依次执行每一步
3. **Evaluate**: `evaluator.py` 判断执行结果是否正常，是否需要触发重规划
4. **Replan**: 需重规划时，`replanner.py` 根据已完成/未完成/失败原因重新制定计划

## 运行

```bash
py -3.9 main.py
```

> 注意：Windows 下 `python` 命令可能指向 Microsoft Store 占位程序，建议用 `py -3.9`

## 重点注意事项

1. **llm.py 路径处理**：通过 `sys.path.insert` 引入上层 `config.py` 和 `day01-agent-loop/.venv`，无法直接 `python main.py` 运行（需要使用 `py -3.9 main.py`）
2. **启用了动态规划**：代码同时保留 `create_plan_static` / `replan_static` 作为静态版本对照，当前注释掉静态版本


## 知识点对应

本示例对应 **AI Agent 规划（Planning）** 模块知识：

| 概念 | 对应代码 |
|---|---|
| 目标拆解 (Task Decomposition) | `planner.py` → LLM 将用户目标拆为子步骤 |
| 顺序执行 (Sequential Execution) | `main.py` while 循环 `pop(0)` 逐项执行 |
| 结果评估 (Evaluation) | `evaluator.py` → 根据执行结果判断是否需重规划 |
| 失败处理与重规划 (Replanning) | `replanner.py` → 失败后重新生成步骤列表 |
| Agent 状态跟踪 (State Tracking) | `state.py` → 维护目标/步骤/完成/失败 |
