# Day04 — Planning（计划与重规划）

## 知识点

AI Agent 的**规划能力**：将大目标自动拆解为可执行步骤，并按 Plan → Execute → Evaluate → Replan 循环推进。这是 Agent 从"被动响应"到"主动规划"的关键升级。

## 文件说明

| 文件 | 职责 |
|---|---|
| `Planner.cs` | 目标拆解：静态硬编码 / LLM 动态生成步骤列表 |
| `Executor.cs` | 步骤执行器：模拟执行，特定步骤（"学习LangChain"）触发失败 |
| `Evaluator.cs` | 结果评估：判断是否需触发重规划 |
| `Replanner.cs` | 失败重规划：静态 / LLM 动态重新生成后续计划 |
| `Program.cs` | Plan → Execute → Evaluate → Replan 主循环 |

## 运行

```bash
dotnet run --project Day04.Planning
```

## 执行流程

```
                            目标
                             ↓
                      Planner 拆解步骤
                             ↓
                    ┌─── Executor 执行步骤
                    │         ↓
                    │   Evaluator 评估结果
                    │      ↙     ↘
                    │  成功       失败/需重规划
                    │    ↓           ↓
                    │  继续下一步   Replanner 重新规划
                    │                ↓
                    └──────── ← 新步骤列表
                             ↓
                        输出结果
```

## 关键细节

- **动态规划**：`Planner.CreatePlanDynamic` 让 LLM 将目标拆为步骤列表（JSON 格式），当前为默认启用
- **静态规划**：`Planner.CreatePlanStatic` 提供硬编码对照，当前注释未用
- **失败触发**：`Executor.ExecuteStep` 中步骤 `"学习LangChain"` 会返回失败，触发 `Replanner` 重新规划
- **状态追踪**：`AgentState` 维护目标、步骤列表、已完成、已失败，贯穿整个生命周期
