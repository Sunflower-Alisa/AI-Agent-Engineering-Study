# Experiments

本目录包含 AI Agent 工程化的系列实验代码。

## config.py 说明

`config.py` 是全局配置文件，统一管理 LLM 提供商配置。它通过环境变量动态选择：

| 环境变量 | 说明 | 默认值 |
|---------|------|--------|
| `LLM_PROVIDER` | 选择 LLM 提供商：`deepseek` 或 `openai` | `deepseek` |
| `DEEPSEEK_API_KEY` | DeepSeek API 密钥 | - |
| `OPENAI_API_KEY` | OpenAI API 密钥 | - |

使用方法：各实验中的 `agent.py` 通过 `from config import api_key, MODEL, cfg` 引入配置，无需在每个文件中重复写 API 地址和密钥。

## 目录结构

```
experiments-py/
├── README.md          ← 本文件
├── config.py          ← 全局 LLM 配置（API 密钥、模型、地址）
├── .venv/             ← 统一虚拟环境（chromadb + openai）
│
├── week01/            ← 第一周：Agent 基础
│   ├── day01-agent-loop/      ← Agent Loop 基础实现
│   ├── day02-tool-calling/    ← Tool Calling 实现
│   ├── day03-memory/          ← Memory 记忆模块
│   ├── day04-planning/        ← Planning 计划与重规划
│   └── day05-decision/        ← Decision 决策模块
│
├── week02/            ← 第二周：系统化 Agent
│   ├── day08-agent-tool-system/ ← 工具系统 + 反思（Tool Calling / ReAct / Reflection）
│   └── day11-rag-agent/         ← RAG 知识库 Agent（Loader→Chunk→Embedding→VectorDB→Retriever）
│
└── week03/            ← 第三周：综合与图编排
    ├── day15-rag-agent/         ← Agent + RAG 综合（规划/执行/决策/反思 + knowledge_search 工具）
    └── day18-langgraph-agent/   ← LangGraph 状态图 Agent（StateGraph 节点 + 条件路由）
```

## 各 day 说明

| day | 主题 | 关键文件 |
|---|---|---|
| day01 | Agent 基础循环 | `agent.py` + `tools.py` |
| day02 | 工具调用选择器 | `agent.py` / `main.py` / `tools.py` |
| day03 | 记忆模块 | `memory.py` / `agent_with_memory.py` |
| day04 | 计划与重规划 | `planner.py` / `replanner.py` |
| day05 | 决策模块 | `decision.py` |
| day08 | 工具系统 + 反思 | `agent.py` / `decision.py` / `actionrouter.py` / `generator.py` / `reflection/` |
| day11 | RAG 知识库 Agent | `rag/`（loader / chunker / vector_store / rag_pipeline / llm） |
| day15 | Agent + RAG 综合 | `agent/` / `rag/` / `tools/` / `reflection/` / `memory/` |
| day18 | LangGraph 状态图 Agent | `agent/`（graph / nodes / router / state / prompt / llm） |

## 运行

所有实验共用 `experiments-py/.venv` 统一虚拟环境（已安装 chromadb + openai）。
通过 site-packages 中的 `experiments.pth` 自动将 `experiments-py/` 加入 sys.path，因此各 .py 无需再做环境引入。

```bash
# 设置 API 密钥
set DEEPSEEK_API_KEY=sk-xxx

# 用统一 venv 运行对应实验
cd week03/day15-rag-agent
..\..\.venv\Scripts\python.exe main.py

# 或激活 venv 后直接运行
..\..\.venv\Scripts\activate
python main.py
```

> - day11 / day15 使用 chroma 向量库，首次运行会下载 MiniLM 嵌入模型（约 79MB，仅一次）
> - day15 的 `main.py` 直接运行时会在顶部 `sys.path.insert` 注入项目根目录，保证绝对导入可用
