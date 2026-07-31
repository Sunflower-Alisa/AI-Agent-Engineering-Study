# Day 01: Agent Loop

学习目标：理解 Agent 的核心运行循环，实现 Observe → Think → Act 的闭环。

## Agent Loop 概念

Agent Loop 是 Agent 的核心控制机制，使 Agent 能够反复执行"观察→思考→行动"的循环，直到完成任务。

```
User
  ↓
Observe（观察用户输入）
  ↓
Think （LLM 推理决策）
  ↓
Act   （调用工具执行）
  ↓
Observe（观察执行结果）
  ↓
Think （继续推理，判断是否完成）
  ↓
  ...（循环直到完成）
  ↓
Answer（最终输出）
```

Agent = LLM + Memory + Tools + Loop + Decision

## 文件结构

```
day01-agent-loop/
├── agent.py          ← Agent 核心实现（Observe / Think / Act 循环）
├── tools.py          ← 工具定义（get_time、calculate）
└── README.md
```

## 运行

```bash
cd experiments-py/week01/day01-agent-loop
..\..\.venv\Scripts\python.exe agent.py
```



