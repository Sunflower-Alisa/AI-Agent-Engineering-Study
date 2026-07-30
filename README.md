# AI-Agent-Engineering-Study

AI Agent 工程化学习与实践，包含 Python 和 .NET 双版本实现。

## 项目结构

```
├── experiments-py/       # Python 版实验代码
│   └── week01/
│       ├── day01-agent-loop/     # Agent 基础循环
│       ├── day02-tool-calling/   # 工具调用
│       ├── day03-memory/         # 记忆模块
│       └── day04-planning/       # 计划与重规划
│
├── experiments-.net/     # .NET 版实验代码
│   ├── AiAgent.Shared/           # 共享抽象层
│   ├── Day01.AgentLoop/          # Agent 基础循环
│   ├── Day02.ToolCalling/        # 工具调用
│   ├── Day03.Memory/             # 记忆模块
│   └── Day04.Planning/           # 计划与重规划
│
└── notes/                # 学习笔记
```

## 运行

```bash
# Python (需要 DEEPSEEK_API_KEY 环境变量)
cd experiments-py/week01/dayXX-xxx && py -3.9 main.py

# .NET
cd experiments-.net && dotnet run --project DayXX.xxxx
```
