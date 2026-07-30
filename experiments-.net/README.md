# AI Agent Engineering — .NET 实现

Python 版 [AI-Agent-Engineering-Study](../experiments-py) 对应的 .NET 实现，覆盖 AI Agent 四大核心模块。

## 项目结构

```
experiments-.net/
├── AiAgentEngineering.slnx           # 解决方案文件
├── README.md                         # 本文件
│
├── AiAgent.Shared/                   # 共享抽象层（类库）
│   ├── ILlmClient.cs                 # LLM 调用接口
│   ├── LlmClient.cs                  # OpenAI 兼容 API 实现（HttpClient）
│   ├── Models.cs                     # ChatMessage / ToolCall / ToolDefinition / AgentState
│   └── AppConfig.cs                  # 环境变量配置（DEEPSEEK_API_KEY 等）
│
├── Day01.AgentLoop/                  # Agent 基础循环
│   ├── Agent.cs                      # observe → think → act → run
│   └── Program.cs                    # 交互式入口
│
├── Day02.ToolCalling/                # 工具调用（Function Calling）
│   ├── Agent.cs                      # tool_calls 解析 + 分发
│   ├── Tools.cs                      # calculate / get_time 工具定义
│   └── Program.cs                    # 交互式入口
│
├── Day03.Memory/                     # 记忆模块
│   ├── MemoryStore.cs                # 基于 JSON 文件的持久化存储
│   ├── AgentWithMemory.cs            # 代码控制型记忆
│   ├── MemoryToolAgent.cs            # Tool 决策型记忆
│   └── Program.cs                    # 模式选择入口
│
└── Day04.Planning/                   # 计划与重规划引擎
    ├── Planner.cs                    # 目标拆解（静态 / LLM 动态）
    ├── Executor.cs                   # 步骤执行
    ├── Evaluator.cs                  # 结果评估
    ├── Replanner.cs                  # 失败重规划
    └── Program.cs                    # Plan → Execute → Evaluate → Replan
```

## 对应关系

| Day | 知识点 | .NET 关键文件 |
|---|---|---|
| Day01 | Agent 基础循环 | `Agent.cs` — while 循环：LLM 决定调工具还是直接回答 |
| Day02 | Tool Calling | `Tools.cs` — Function Calling 定义；`Agent.cs` — tool_calls 分发 |
| Day03 | 记忆 (Memory) | `MemoryStore.cs` — 持久化；两种集成模式 |
| Day04 | 规划 (Planning) | `Planner → Executor → Evaluator → Replanner` 四段式流水线 |

## 运行要求

- .NET 10.0+ SDK
- 环境变量 `DEEPSEEK_API_KEY` 或 `OPENAI_API_KEY`（设 `LLM_PROVIDER=openai` 切换）

```bash
# 运行某个项目
dotnet run --project Day01.AgentLoop
dotnet run --project Day02.ToolCalling
dotnet run --project Day03.Memory
dotnet run --project Day04.Planning
```
