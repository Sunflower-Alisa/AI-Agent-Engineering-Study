# AI-Agent-Engineering-Study

AI Agent 工程化学习与实践，包含 Python 和 .NET 双版本实现。

## 项目结构

```
├── experiments-py/       # Python 版实验代码
│   └── week01/
│       ├── day01-agent-loop/     # Agent 基础循环
│       ├── day02-tool-calling/   # 工具调用
│       ├── day03-memory/         # 记忆模块
│       ├── day04-planning/       # 计划与重规划
│       ├── day05-decision/       # 决策模块
│       ├── day08-agent-tool-system/ # 工具系统 + 反思 (Tool Calling / ReAct / Reflection)
│       └── day11-rag-agent/      # RAG 知识库 Agent (Loader → Chunk → Embedding → VectorDB → Retriever)
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

## Python 各 day 说明

| day | 主题 | 关键文件 |
|---|---|---|
| day01 | Agent 基础循环 | `agent.py` + `tools.py` |
| day02 | 工具调用选择器 | `agent.py` / `main.py` / `tools.py` |
| day03 | 记忆模块 | `memory.py` / `agent_with_memory.py` / `memory_tools_agent.py` |
| day04 | 计划与重规划 | `planner.py` / `replanner.py` |
| day05 | 决策模块 | `decision.py` |
| day08 | 工具系统 + 反思 | `agent.py` / `decision.py` / `actionrouter.py` / `generator.py` / `reflection/` |
| day11 | RAG 知识库 Agent | `rag/` (loader / chunker / vector_store / rag_pipeline / llm) |

## 运行

```bash
# Python (需要 DEEPSEEK_API_KEY 环境变量)
cd experiments-py/week01/dayXX-xxx && py -3.9 main.py

# .NET
cd experiments-.net && dotnet run --project DayXX.xxxx
```

> Python 统一使用 `experiments-py/.venv`（Python 3.9，通过 `.pth` 自动引入 `config.py`），运行示例：
> ```bash
> cd experiments-py/week01/day11-rag-agent && ..\..\.venv\Scripts\python.exe main.py
> ```
> day11 首次运行 chroma 会下载 MiniLM 嵌入模型（79MB，断网/慢速可改用 `curl -C -` 续传到位后自动复用缓存）。
